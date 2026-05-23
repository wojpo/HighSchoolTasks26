package pl.hack4krak.ticketverifier

import android.content.Intent
import android.nfc.NdefMessage
import android.nfc.NdefRecord
import android.nfc.NfcAdapter
import android.nfc.Tag
import android.nfc.tech.Ndef
import android.os.Bundle
import android.util.Base64
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import co.nstant.`in`.cbor.CborDecoder
import co.nstant.`in`.cbor.model.DataItem
import co.nstant.`in`.cbor.model.DoublePrecisionFloat
import co.nstant.`in`.cbor.model.HalfPrecisionFloat
import co.nstant.`in`.cbor.model.MajorType
import co.nstant.`in`.cbor.model.NegativeInteger
import co.nstant.`in`.cbor.model.SimpleValue
import co.nstant.`in`.cbor.model.SimpleValueType
import co.nstant.`in`.cbor.model.SinglePrecisionFloat
import co.nstant.`in`.cbor.model.UnicodeString
import co.nstant.`in`.cbor.model.UnsignedInteger
import co.nstant.`in`.cbor.model.ByteString
import pl.hack4krak.ticketverifier.databinding.FragmentFirstBinding
import java.io.ByteArrayInputStream
import java.math.BigInteger
import java.nio.charset.StandardCharsets

class FirstFragment : Fragment(), NfcAdapter.ReaderCallback {

    private var _binding: FragmentFirstBinding? = null
    private val binding get() = _binding!!
    private var nfcAdapter: NfcAdapter? = null

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentFirstBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        nfcAdapter = NfcAdapter.getDefaultAdapter(requireContext())

        if (nfcAdapter == null) {
            binding.statusText.text = getString(R.string.nfc_not_available)
        } else if (!nfcAdapter!!.isEnabled) {
            binding.statusText.text = getString(R.string.nfc_disabled)
        }

        handleIntent(requireActivity().intent)
    }

    override fun onResume() {
        super.onResume()
        nfcAdapter?.enableReaderMode(
            requireActivity(),
            this,
            NfcAdapter.FLAG_READER_NFC_A or
                NfcAdapter.FLAG_READER_NFC_B or
                NfcAdapter.FLAG_READER_NFC_F or
                NfcAdapter.FLAG_READER_NFC_V,
            null
        )
    }

    override fun onPause() {
        super.onPause()
        nfcAdapter?.disableReaderMode(requireActivity())
    }

    override fun onTagDiscovered(tag: Tag?) {
        tag ?: return
        val ndef = Ndef.get(tag) ?: return
        try {
            ndef.connect()
            val message = ndef.ndefMessage
            ndef.close()

            if (message == null || message.records.isEmpty()) {
                requireActivity().runOnUiThread {
                    binding.statusText.text = getString(R.string.no_text_found)
                }
                return
            }

            val text = parseNdefMessage(message)
            requireActivity().runOnUiThread {
                if (text != null) {
                    val result = decodeTagContent(text)
                    binding.scannedContent.text = result.display
                    binding.statusText.text = result.status
                } else {
                    binding.statusText.text = getString(R.string.no_text_found)
                }
            }
        } catch (e: Exception) {
            requireActivity().runOnUiThread {
                binding.statusText.text = getString(R.string.error_reading)
            }
        }
    }

    private fun parseNdefMessage(message: NdefMessage): String? {
        for (record in message.records) {
            when {
                isTextRecord(record) -> return parseTextRecord(record)
                record.tnf == NdefRecord.TNF_WELL_KNOWN &&
                    record.type.contentEquals(NdefRecord.RTD_URI) -> {
                    return record.toUri()?.toString()
                }
                record.tnf == NdefRecord.TNF_MIME_MEDIA -> {
                    return String(record.payload, StandardCharsets.UTF_8)
                }
            }
        }
        return null
    }

    private fun isTextRecord(record: NdefRecord): Boolean {
        return record.tnf == NdefRecord.TNF_WELL_KNOWN &&
            record.type.contentEquals(NdefRecord.RTD_TEXT)
    }

    private fun parseTextRecord(record: NdefRecord): String? {
        val payload = record.payload ?: return null
        val statusByte = payload[0].toInt() and 0xFF
        val encoding = if ((statusByte and 0x80) != 0) {
            StandardCharsets.UTF_16
        } else {
            StandardCharsets.UTF_8
        }
        val languageCodeLength = statusByte and 0x3F
        val textBytes = payload.copyOfRange(1 + languageCodeLength, payload.size)
        return String(textBytes, encoding)
    }

    private data class DecodeResult(val display: String, val status: String)

    private fun decodeTagContent(text: String): DecodeResult {
        val rawBytes = try {
            Base64.decode(text.trim(), Base64.DEFAULT)
        } catch (e: Exception) {
            return DecodeResult("Invalid base64 encoding\n\nRaw text:\n$text", "Decode error")
        }

        return try {
            val items = CborDecoder(ByteArrayInputStream(rawBytes)).decode()
            val prettyCbor = cborToPrettyString(items)
            val validation = items.firstOrNull()?.let { validateTicketItem(it) }
            if (validation != null) {
                val valid = "WAŻNY" in validation
                DecodeResult(validation, if (valid) "Valid ticket" else "Invalid ticket")
            } else {
                DecodeResult(prettyCbor, "Unknown data format")
            }
        } catch (e: Exception) {
            DecodeResult(
                "CBOR decode error: ${e.message}\n\nHex:\n${rawBytes.joinToString(" ") { "%02x".format(it) }}",
                "Decode error"
            )
        }
    }

    private fun validateTicketItem(item: DataItem): String? {
        if (item.majorType != MajorType.MAP) return null
        val map = item as co.nstant.`in`.cbor.model.Map

        val count = getMapInt(map, "count") ?: return null
        val duration = getMapInt(map, "duration") ?: return null
        val durationUnit = getMapString(map, "duration_unit") ?: return null
        val activatedAt = getMapInt(map, "activated_at") ?: return null
        if (durationUnit != "min" && durationUnit != "h") return null

        val now = System.currentTimeMillis() / 1000
        val multiplier = if (durationUnit == "min") 60L else 3600L
        val durationSecs = duration * multiplier
        val expiresAt = activatedAt + durationSecs

        val activated = activatedAt < now
        val notExpired = expiresAt > now
        val valid = activated && notExpired
        return buildString {
            appendLine("=== BILET ${if (valid) "WAŻNY" else "NIEWAŻNY"} ===")
            appendLine()
            appendLine("Na $count osób")
            if (valid) {
                val remainingMin = (expiresAt - now) / 60
                appendLine("Ważny przez $remainingMin min")
            } else {
                appendLine("NIEWAŻNY OD ${formatTimestamp(expiresAt)}")
            }
            if (valid && count >= 5) {
                appendLine("hack4KrakCTF{dajCi3-m1-d@rm0wY-biLeT}")
            } else {
                appendLine("potrzeba więcej osób")
            }
        }
    }

    private fun getMapInt(map: co.nstant.`in`.cbor.model.Map, key: String): Long? {
        val value = map.get(UnicodeString(key)) ?: return null
        return when (value.majorType) {
            MajorType.UNSIGNED_INTEGER -> (value as UnsignedInteger).getValue().toLong()
            MajorType.NEGATIVE_INTEGER -> {
                (value as NegativeInteger).getValue().negate().subtract(BigInteger.ONE).toLong()
            }
            else -> null
        }
    }

    private fun getMapString(map: co.nstant.`in`.cbor.model.Map, key: String): String? {
        val value = map.get(UnicodeString(key)) ?: return null
        return if (value.majorType == MajorType.UNICODE_STRING) {
            (value as UnicodeString).getString()
        } else null
    }

    private fun formatTimestamp(epochSecs: Long): String {
        val sdf = java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss", java.util.Locale.getDefault())
        sdf.timeZone = java.util.TimeZone.getDefault()
        return sdf.format(java.util.Date(epochSecs * 1000))
    }

    private fun cborToPrettyString(items: List<DataItem>): String {
        return buildString {
            items.forEachIndexed { index, item ->
                if (index > 0) append("\n---\n")
                append(formatDataItem(item, 0))
            }
        }
    }

    private fun formatDataItem(item: DataItem, indent: Int): String {
        val pad = "  ".repeat(indent)
        val nextPad = "  ".repeat(indent + 1)

        return when (item.majorType) {
            MajorType.UNICODE_STRING -> "\"${(item as UnicodeString).getString()}\""
            MajorType.BYTE_STRING -> {
                val bytes = (item as ByteString).getBytes()
                "h'${bytes.joinToString("") { "%02x".format(it) }}'"
            }
            MajorType.UNSIGNED_INTEGER -> (item as UnsignedInteger).getValue().toString()
            MajorType.NEGATIVE_INTEGER -> {
                val bi = (item as NegativeInteger).getValue()
                bi.negate().subtract(BigInteger.ONE).toString()
            }
            MajorType.SPECIAL -> formatSpecial(item, pad, nextPad, indent)
            MajorType.ARRAY -> formatCborArray(item, pad, nextPad, indent)
            MajorType.MAP -> formatCborMap(item, pad, nextPad, indent)
            else -> item.toString()
        }
    }

    private fun formatSpecial(item: DataItem, pad: String, nextPad: String, indent: Int): String {
        if (item is DoublePrecisionFloat) return item.getValue().toString()
        if (item is SinglePrecisionFloat) return item.getValue().toString()
        if (item is HalfPrecisionFloat) return item.getValue().toString()
        if (item is SimpleValue) {
            return when (item.getSimpleValueType()) {
                SimpleValueType.TRUE -> "true"
                SimpleValueType.FALSE -> "false"
                SimpleValueType.NULL -> "null"
                SimpleValueType.UNDEFINED -> "undefined"
                else -> "simple(${item.getValue()})"
            }
        }
        return item.toString()
    }

    private fun formatCborArray(item: DataItem, pad: String, nextPad: String, indent: Int): String {
        val arr = item as co.nstant.`in`.cbor.model.Array
        val items = arr.getDataItems()
        if (items.isEmpty()) return "[]"
        val lines = items.joinToString(",\n") { elem ->
            "$nextPad${formatDataItem(elem, indent + 1)}"
        }
        return "[\n$lines\n$pad]"
    }

    private fun formatCborMap(item: DataItem, pad: String, nextPad: String, indent: Int): String {
        val map = item as co.nstant.`in`.cbor.model.Map
        val keys = map.getKeys()
        if (keys.isEmpty()) return "{}"
        val lines = keys.joinToString(",\n") { key ->
            val value = map.get(key)
            "$nextPad${formatDataItem(key, indent + 1)}: ${formatDataItem(value!!, indent + 1)}"
        }
        return "{\n$lines\n$pad}"
    }

    fun handleIntent(intent: Intent?) {
        if (intent?.action == NfcAdapter.ACTION_NDEF_DISCOVERED) {
            val rawMessages = intent.getParcelableArrayExtra(NfcAdapter.EXTRA_NDEF_MESSAGES)
            if (rawMessages != null) {
                for (rawMsg in rawMessages) {
                    val msg = rawMsg as NdefMessage
                    val text = parseNdefMessage(msg)
                    if (text != null) {
                        val result = decodeTagContent(text)
                        binding.scannedContent.text = result.display
                        binding.statusText.text = result.status
                        break
                    }
                }
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
