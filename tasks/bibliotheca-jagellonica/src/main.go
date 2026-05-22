package main

import (
	"fmt"
	"hash/fnv"
	"html/template"
	"io"
	"log"
	"net/http"
	"os"
	"regexp"
	"strconv"
	"strings"
	"time"
)

const (
	defaultPort     = "8080"
	virtualBookSize = int64(8) * 1024 * 1024
	finalBookSize   = int64(37) * 1000 * 1000 * 1000 * 1000
	maxRangeBytes   = int64(1024 * 1024)
)

var (
	roomPattern = regexp.MustCompile(`^[0-9a-f]{16,64}$`)
	bookPattern = regexp.MustCompile(`^[a-z0-9][a-z0-9-]{0,63}$`)
	pageModTime = time.Date(2026, 5, 17, 12, 0, 0, 0, time.UTC)
)

var virtualOverlays = map[string]map[int64]string{
	"ffffffffffffffffffffffffffffffff/4/5/32/umbra": {
		finalBookSize - 512: "Karta krancowa nie jest zakonczeniem, lecz odciskiem katalogu. Piec ekslibrisow ma postac POCZATEK:DLUGOSC. Uloz je wedlug porzadku wpisu, nie wedlug wielkosci liczb. BABEL 13371337:13; E 27182818:10; PI 31415926:9; FI 16180339:11; KRAKOW 42424242:13.\n",
		13371337:            "hack4KrakCTF{",
		27182818:            "c4t4l0gu5_",
		31415926:            "in_umbra_",
		16180339:            "ranges_non_",
		42424242:            "legunt_totum}",
	},
}

type manuscript struct {
	Ref     bookRef
	Title   string
	Body    string
	Listed  bool
	Headers map[string]string
}

var manuscripts = []manuscript{
	{
		Ref:    bookRef{Room: "0123456789abcdef0123456789abcdef", Wall: 2, Shelf: 4, Volume: 17, Book: "prolog"},
		Title:  "Prolog kustosza",
		Listed: true,
		Body: strings.TrimSpace(`Pierwsze kłamstwo czytelni Bibliotheca Jagellonica brzmi: książkę należy przeczytać od początku.

Drugie kłamstwo brzmi: jeżeli tytułu nie ma w katalogu, to nie istnieje. Nieskończona biblioteka nigdy nie kłamie wprost; ona tylko drukuje wszystkie fałszywe drogi obok jednej prawdziwej.

Na pierwszym marginesie stoi zwierzę z miasta Buffalo. Na drugim - kanclerz z Verulamu. Obydwaj udają, że mówią o gramatyce.`),
	},
	{
		Ref:    bookRef{Room: "0123456789abcdef0123456789abcdef", Wall: 2, Shelf: 4, Volume: 17, Book: "buffalo"},
		Title:  "Bison bonasus, przepisany w Buffalo",
		Listed: true,
		Body: strings.TrimSpace(`Zdanie jest poprawne tylko wtedy, gdy czytelnik przestaje widzieć słowa, a zaczyna widzieć ich skóry.

W stadzie poniżej każdy bizon ma ten sam kształt, lecz nie ten sam grzbiet. Verulam wiedział, że alfabet może ukryć się w dwóch krojach pisma.

		buffalo Buffalo buffalo Buffalo buffalo
		buffalo Buffalo Buffalo buffalo Buffalo
		Buffalo buffalo buffalo buffalo buffalo
		buffalo buffalo Buffalo buffalo buffalo
		buffalo Buffalo buffalo Buffalo Buffalo

https://www.youtube.com/watch?v=ejgyHIClRoU`),
	},
	{
		Ref:   bookRef{Room: "0123456789abcdef0123456789abcdef", Wall: 2, Shelf: 4, Volume: 17, Book: "lorem"},
		Title: "Palimpsest lorem",
		Body: strings.TrimSpace(`Kanon powtarza się bez końca, dlatego fałsz nie potrzebuje wielkiej litery.

Kanon:
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

Odpis:
Lorem ipsum dolor sit amet, qonsectetur adipiscing elit, sed do eiuismod tempor incididunt ut labore et dolore magna aliqua.

Babel nie jest miejscem, lecz kluczem do obcego alfabetu.

Na marginesie kustosz dopisał jeszcze jeden odsyłacz. Notatka jest zapieczętowana i atrament metaliczny; bez właściwego klucza pozostanie szumem:
/library/0ddba11ad0ddba11ad0ddba11ad0ddba11ad/wall/1/shelf/2/volume/9/book/cipher.txt`),
	},
	{
		Ref:   bookRef{Room: "0123456789abcdef0123456789abcdef", Wall: 2, Shelf: 4, Volume: 17, Book: "pi"},
		Title: "tabula circuli",
		Body: strings.TrimSpace(`kiedy liczba jest przepisywana zbyt długo, niektóre cyfry przestają być cyframi.

3141592653589793238462643383279502884197169399375105P8209749445923078164062862089986280348253421170679821O4808651328230664709384460955058223172535940812848111L7450284102701938521105559644622948954930381964428810Y9756659334461284756482337867831652712019091456485669G2346034861045432664821339360726024914127372458700660L6315588174881520920962829254091715364367892590360011O3305305488204665213841469519415116094330572703657595T9195309218611738193261179310511854807446237996274956;3141 L7351885752724891227938183011949129833673362440656643I0860213949463952247371907021798609437027705392171762N9317675238467481846766940513200056812714526356082778G5771342757789609173637178721468440901224953430146549U5853710507922796892589235420199561121290219608640344A1815981362977477130996051870721134999999837297804995 R1059731732816096318595024459455346908302642522308253O3446850352619311881710100031378387528865875332083814M2061717766914730359825349042875546873115956286388235A3787593751957781857780532171226806613001927876611195E9092164201989

karta kończy się tam, gdzie kończą się cyfry.`),
	},
	{
		Ref:   bookRef{Room: "0123456789abcdef0123456789abcdef", Wall: 2, Shelf: 4, Volume: 17, Book: "polyglot"},
		Title: "Liber peregrinus",
		Body: strings.TrimSpace(`Jedna księga, kilka języków i pieczęć starej akademii.

pl: nie każde tłumaczenie zachowuje porządek katalogu
en: not every translation preserves the order of the catalogue
eo: ne cxiu traduko konservas la ordon de la katalogo
la: non omnis translatio ordinem catalogi servat

Język zwykły daje treść zwykłą. Język katalogów otwiera kartę, którą bibliotekarz wypełnił poza tekstem.`),
	},
	{
		Ref:   bookRef{Room: "0123456789abcdef0123456789abcdef", Wall: 2, Shelf: 4, Volume: 17, Book: "headers"},
		Title: "Karta bez tresci widzialnej",
		Body: strings.TrimSpace(`Widzialne folio jest prawie puste, a więc prawie uczciwe.

Niektórzy kustosze piszą odsyłacze na papierze. Inni w miejscu, które widzi tylko posłaniec niosący odpowiedź.`),
		Headers: map[string]string{
			"Link": `</library/ffffffffffffffffffffffffffffffff/wall/4/shelf/5/volume/32/book/umbra.txt>; rel="next"`,
		},
	},
	{
		Ref:   bookRef{Room: "0ddba11ad0ddba11ad0ddba11ad0ddba11ad", Wall: 1, Shelf: 2, Volume: 9, Book: "cipher"},
		Title: "Catalogus clausus",
		Body: strings.TrimSpace(`Zamknięta notatka została przepisana zanim opisano jej klucz.

24282c2420424e0e0c0e1000101c43040704030a040704030a040704030a040704030a040704030a040704030a04074d120d0e0d4d5143110907090a4d544d13030e140f004351534d07030d0a4d10010013034b181a15425e4c1114040c07114157545e425a42150316040f450f1818160406420a0317181b411845070d0f01045642232327292e4153565f555051565b585051494c274150525d5a535a5454585052494c322842565d5650575c5e545b5b494c242842545a535952565f5b5b535440422a3024272d3642515e5653565758505b535642

Zdejmij metaliczny atrament. Klucz jest wspólny z tym, który otwierał obcy alfabet.`),
	},
}

var pageTemplate = template.Must(template.New("page").Parse(`<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{.Title}}</title>
  <style>
    :root { color-scheme: light; --ink:#211b14; --muted:#746650; --paper:#f3ead7; --line:#c9b994; --red:#7d1c1c; }
    * { box-sizing: border-box; }
    body { margin:0; min-height:100vh; color:var(--ink); background:radial-gradient(circle at 20% 0%, #fff8e8 0, var(--paper) 34rem, #ded0ad 100%); font-family: Georgia, 'Times New Roman', serif; }
    body:before { content:""; position:fixed; inset:0; pointer-events:none; opacity:.16; background-image:linear-gradient(90deg, #000 1px, transparent 1px), linear-gradient(#000 1px, transparent 1px); background-size:34px 34px; mix-blend-mode:multiply; }
    main { width:min(980px, calc(100% - 32px)); margin:0 auto; padding:52px 0 72px; }
    .seal { width:76px; height:76px; border:2px solid var(--red); border-radius:50%; display:grid; place-items:center; color:var(--red); font-size:34px; margin-bottom:34px; box-shadow:0 0 0 9px rgba(125,28,28,.07); }
    h1 { font-size:clamp(42px, 8vw, 92px); line-height:.88; letter-spacing:-.055em; max-width:780px; margin:0 0 24px; font-weight:500; }
    p, li { font-size:20px; line-height:1.62; }
    .lead { max-width:760px; color:#3a3023; font-size:23px; }
    .panel { margin-top:36px; border:1px solid var(--line); background:rgba(255,252,242,.62); box-shadow:0 22px 70px rgba(69,50,22,.16); padding:28px; }
    code, pre { font-family:'Courier New', monospace; }
    code { background:#eadfc5; padding:.16em .36em; border:1px solid #d5c49d; }
    pre { overflow:auto; padding:20px; border:1px dashed var(--line); background:#fff8e6; }
    a { color:var(--red); text-decoration-thickness:1px; text-underline-offset:4px; }
    .grid { display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:18px; margin-top:24px; }
    .card { border-left:4px solid var(--red); padding:16px 18px; background:rgba(255,255,255,.38); }
    .muted { color:var(--muted); }
  </style>
</head>
<body><main>{{.Body}}</main></body>
</html>`))

func main() {
	mux := newServer()
	port := os.Getenv("PORT")
	if port == "" {
		port = defaultPort
	}
	addr := ":" + port
	log.Printf("bibliotheca listening on %s", addr)
	log.Fatal(http.ListenAndServe(addr, mux))
}

func newServer() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("/", handleHome)
	mux.HandleFunc("/robots.txt", handleRobots)
	mux.HandleFunc("/catalog", handleCatalog)
	mux.HandleFunc("/library/", handleVirtualBook)
	return blockCrawlerAgents(mux)
}

// blockedCrawlerAgents is the single source of truth for both the blocking middleware and robots.txt.
var blockedCrawlerAgents = []string{
	"GPTBot",
	"ChatGPT-User",
	"OAI-SearchBot",
	"ClaudeBot",
	"Claude-User",
	"anthropic-ai",
	"CCBot",
	"Google-Extended",
	"PerplexityBot",
	"Bytespider",
	"Applebot-Extended",
	"Amazonbot",
}

func blockCrawlerAgents(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		userAgent := strings.ToLower(r.UserAgent())
		for _, agent := range blockedCrawlerAgents {
			if strings.Contains(userAgent, strings.ToLower(agent)) {
				w.Header().Set("X-Robots-Tag", "noindex, nofollow, noarchive, nosnippet, noimageindex, noai, noimageai")
				http.Error(w, "crawler access is not allowed", http.StatusForbidden)
				return
			}
		}
		next.ServeHTTP(w, r)
	})
}

func handleHome(w http.ResponseWriter, r *http.Request) {
	if r.URL.Path != "/" {
		http.NotFound(w, r)
		return
	}
	if !methodAllowed(w, r, http.MethodGet, http.MethodHead) {
		return
	}
	body := template.HTML(`<div class="seal">BJ</div>
<h1>Bibliotheca Jagellonica</h1>
<p class="lead">Imitacja nieskończonej biblioteki: skończone manuskrypty ukryte między deterministycznymi, absurdalnie wielkimi woluminami.</p>
<section class="panel">
	  <p>Zacznij od <a href="/catalog">katalogu</a>. Tragarze odmawiają niemożliwych woluminów, lecz tolerują wąskie okna.</p>
	  <p class="muted">Każdy dokument wart czytania pozostaje księgą <code>.txt</code>.</p>
</section>`)
	renderPage(w, r, "Bibliotheca Jagellonica", body)
}

func handleRobots(w http.ResponseWriter, r *http.Request) {
	if r.URL.Path != "/robots.txt" {
		http.NotFound(w, r)
		return
	}
	if !methodAllowed(w, r, http.MethodGet, http.MethodHead) {
		return
	}
	w.Header().Set("Content-Type", "text/plain; charset=utf-8")
	w.Header().Set("X-Robots-Tag", "noindex, nofollow, noarchive, nosnippet, noimageindex, noai, noimageai")
	if r.Method == http.MethodHead {
		return
	}
	_, _ = io.WriteString(w, robotsTxt)
}

func handleCatalog(w http.ResponseWriter, r *http.Request) {
	if r.URL.Path != "/catalog" {
		http.NotFound(w, r)
		return
	}
	if !methodAllowed(w, r, http.MethodGet, http.MethodHead) {
		return
	}
	var cards strings.Builder
	for _, item := range manuscripts {
		if !item.Listed {
			continue
		}
		path := item.Ref.path()
		fmt.Fprintf(&cards, `<article class="card"><h2>%s</h2><p><a href="%s">%s</a></p></article>`, template.HTMLEscapeString(item.Title), path, path)
	}
	body := template.HTML(`<div class="seal">CAT</div>
<h1>Katalog</h1>
<p class="lead">Indeks czytelni. Każdy wpis jest księgą; niektóre księgi są skończone, inne tylko udają, że mają koniec.</p>
<div class="grid">` + cards.String() + `</div>`)
	renderPage(w, r, "Katalog", body)
}

func handleVirtualBook(w http.ResponseWriter, r *http.Request) {
	if !methodAllowed(w, r, http.MethodGet, http.MethodHead) {
		return
	}
	ref, ok := parseBookPath(r.URL.Path)
	if !ok {
		http.NotFound(w, r)
		return
	}
	if item, ok := finiteBook(ref); ok {
		for name, value := range item.Headers {
			w.Header().Set(name, value)
		}
		body := item.Title + "\n\n" + item.Body + "\n"
		if ref.Book == "polyglot" && acceptsLatin(r.Header.Get("Accept-Language")) {
			body += "\nEx libris: /library/0123456789abcdef0123456789abcdef/wall/2/shelf/4/volume/17/book/headers.txt\n"
		}
		serveFiniteText(w, r, ref.filename(), body)
		return
	}
	size := virtualSize(ref)

	w.Header().Set("Accept-Ranges", "bytes")
	w.Header().Set("X-Bibliotheca-Object", "virtual-book")
	w.Header().Set("X-Bibliotheca-Book", ref.Book)
	w.Header().Set("X-Bibliotheca-Size", strconv.FormatInt(size, 10))

	if r.Method == http.MethodHead {
		w.Header().Set("Content-Length", strconv.FormatInt(size, 10))
		w.Header().Set("Content-Type", "text/plain; charset=utf-8")
		return
	}

	rangeHeader := r.Header.Get("Range")
	if rangeHeader == "" {
		if isFinalBook(ref) {
			http.Error(w, "To folio wazy trzydziesci siedem terabajtow. Tragarz nie wydaje calych nieskonczonosci.", http.StatusRequestEntityTooLarge)
			return
		}
		w.Header().Set("Content-Type", "text/plain; charset=utf-8")
		_, _ = io.Copy(w, newVirtualReader(ref.seed(), 0, size))
		return
	}

	byteRange, err := parseRange(rangeHeader, size)
	if err != nil {
		w.Header().Set("Content-Range", fmt.Sprintf("bytes */%d", size))
		http.Error(w, err.Error(), http.StatusRequestedRangeNotSatisfiable)
		return
	}
	if byteRange.length() > maxRangeBytes {
		w.Header().Set("Content-Range", fmt.Sprintf("bytes */%d", size))
		http.Error(w, "Requested window is too large for the reading room.", http.StatusRequestedRangeNotSatisfiable)
		return
	}

	w.Header().Set("Content-Type", "text/plain; charset=utf-8")
	w.Header().Set("Content-Length", strconv.FormatInt(byteRange.length(), 10))
	w.Header().Set("Content-Range", fmt.Sprintf("bytes %d-%d/%d", byteRange.start, byteRange.end, size))
	w.WriteHeader(http.StatusPartialContent)
	_, _ = io.Copy(w, newVirtualReader(ref.seed(), byteRange.start, byteRange.length()))
}

func methodAllowed(w http.ResponseWriter, r *http.Request, methods ...string) bool {
	for _, method := range methods {
		if r.Method == method {
			return true
		}
	}
	w.Header().Set("Allow", strings.Join(methods, ", "))
	http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
	return false
}

func renderPage(w http.ResponseWriter, r *http.Request, title string, body template.HTML) {
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	if r.Method == http.MethodHead {
		return
	}
	_ = pageTemplate.Execute(w, map[string]any{"Title": title, "Body": body})
}

func serveFiniteText(w http.ResponseWriter, r *http.Request, filename string, body string) {
	w.Header().Set("Content-Type", "text/plain; charset=utf-8")
	w.Header().Set("Accept-Ranges", "bytes")
	http.ServeContent(w, r, filename, pageModTime, strings.NewReader(body))
}

func acceptsLatin(header string) bool {
	for _, part := range strings.Split(header, ",") {
		language := strings.ToLower(strings.TrimSpace(strings.SplitN(part, ";", 2)[0]))
		if language == "la" || strings.HasPrefix(language, "la-") {
			return true
		}
	}
	return false
}

type bookRef struct {
	Room   string
	Wall   int
	Shelf  int
	Volume int
	Book   string
}

func (b bookRef) seed() string {
	return fmt.Sprintf("%s/%d/%d/%d/%s", b.Room, b.Wall, b.Shelf, b.Volume, b.Book)
}

func (b bookRef) path() string {
	return fmt.Sprintf("/library/%s/wall/%d/shelf/%d/volume/%d/book/%s.txt", b.Room, b.Wall, b.Shelf, b.Volume, b.Book)
}

func (b bookRef) filename() string {
	return b.Book + ".txt"
}

func finiteBook(ref bookRef) (manuscript, bool) {
	for _, item := range manuscripts {
		if item.Ref == ref {
			return item, true
		}
	}
	return manuscript{}, false
}

func virtualSize(ref bookRef) int64 {
	if isFinalBook(ref) {
		return finalBookSize
	}
	return virtualBookSize
}

func isFinalBook(ref bookRef) bool {
	return ref == bookRef{Room: "ffffffffffffffffffffffffffffffff", Wall: 4, Shelf: 5, Volume: 32, Book: "umbra"}
}

func parseBookPath(path string) (bookRef, bool) {
	parts := strings.Split(strings.Trim(path, "/"), "/")
	if len(parts) != 10 || parts[0] != "library" || parts[2] != "wall" || parts[4] != "shelf" || parts[6] != "volume" || parts[8] != "book" {
		return bookRef{}, false
	}
	room := parts[1]
	name := strings.TrimSuffix(parts[9], ".txt")
	wall, wallOK := parseBoundedInt(parts[3], 1, 4)
	shelf, shelfOK := parseBoundedInt(parts[5], 1, 5)
	volume, volumeOK := parseBoundedInt(parts[7], 1, 32)
	if !roomPattern.MatchString(room) || !bookPattern.MatchString(name) || !strings.HasSuffix(parts[9], ".txt") || !wallOK || !shelfOK || !volumeOK {
		return bookRef{}, false
	}
	return bookRef{Room: room, Wall: wall, Shelf: shelf, Volume: volume, Book: name}, true
}

func parseBoundedInt(raw string, min int, max int) (int, bool) {
	value, err := strconv.Atoi(raw)
	if err != nil || value < min || value > max {
		return 0, false
	}
	return value, true
}

type httpRange struct {
	start int64
	end   int64
}

func (r httpRange) length() int64 {
	return r.end - r.start + 1
}

func parseRange(header string, size int64) (httpRange, error) {
	if !strings.HasPrefix(header, "bytes=") || strings.Contains(header, ",") {
		return httpRange{}, fmt.Errorf("only a single bytes range is supported")
	}
	spec := strings.TrimPrefix(header, "bytes=")
	startRaw, endRaw, ok := strings.Cut(spec, "-")
	if !ok {
		return httpRange{}, fmt.Errorf("invalid range syntax")
	}
	if startRaw == "" {
		suffix, err := strconv.ParseInt(endRaw, 10, 64)
		if err != nil || suffix <= 0 {
			return httpRange{}, fmt.Errorf("invalid suffix range")
		}
		if suffix > size {
			suffix = size
		}
		return httpRange{start: size - suffix, end: size - 1}, nil
	}
	start, err := strconv.ParseInt(startRaw, 10, 64)
	if err != nil || start < 0 || start >= size {
		return httpRange{}, fmt.Errorf("range start outside the virtual book")
	}
	end := size - 1
	if endRaw != "" {
		end, err = strconv.ParseInt(endRaw, 10, 64)
		if err != nil || end < start {
			return httpRange{}, fmt.Errorf("invalid range end")
		}
		if end >= size {
			end = size - 1
		}
	}
	return httpRange{start: start, end: end}, nil
}

type virtualReader struct {
	seed      string
	seedHash  uint64
	position  int64
	remaining int64
}

func newVirtualReader(seed string, start int64, length int64) io.Reader {
	h := fnv.New64a()
	_, _ = h.Write([]byte(seed))
	return &virtualReader{seed: seed, seedHash: h.Sum64(), position: start, remaining: length}
}

func (r *virtualReader) Read(p []byte) (int, error) {
	if r.remaining <= 0 {
		return 0, io.EOF
	}
	if int64(len(p)) > r.remaining {
		p = p[:int(r.remaining)]
	}
	for i := range p {
		p[i] = generatedByte(r.seed, r.seedHash, r.position+int64(i))
	}
	r.position += int64(len(p))
	r.remaining -= int64(len(p))
	return len(p), nil
}

func generatedByte(seed string, seedHash uint64, offset int64) byte {
	if overlay, ok := virtualOverlay(seed, offset); ok {
		return overlay
	}
	if seed == "ffffffffffffffffffffffffffffffff/4/5/32/umbra" && offset >= finalBookSize-512 {
		return ' '
	}
	if strings.HasSuffix(seed, "/buffalo") {
		return repeatingByte("Buffalo buffalo Buffalo buffalo buffalo buffalo Buffalo buffalo. ", offset)
	}
	if strings.HasSuffix(seed, "/lorem") {
		return repeatingByte("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. ", offset)
	}
	if strings.HasSuffix(seed, "/pi") {
		return repeatingByte(piDigits, offset)
	}
	if offset%80 == 79 {
		return '\n'
	}
	// Mix precomputed seed hash with offset using murmur3-style finalisation — no allocations.
	alphabet := "abcdefghijklmnopqrstuvwxyz     ,.;:"
	h := seedHash ^ uint64(offset)
	h ^= h >> 33
	h *= 0xff51afd7ed558ccd
	h ^= h >> 33
	h *= 0xc4ceb9fe1a85ec53
	h ^= h >> 33
	return alphabet[h%uint64(len(alphabet))]
}

func virtualOverlay(seed string, offset int64) (byte, bool) {
	for start, text := range virtualOverlays[seed] {
		if offset >= start && offset < start+int64(len(text)) {
			return text[offset-start], true
		}
	}
	return 0, false
}

func repeatingByte(text string, offset int64) byte {
	return text[offset%int64(len(text))]
}

const piDigits = "31415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679"

var robotsTxt = func() string {
	var sb strings.Builder
	for _, agent := range blockedCrawlerAgents {
		fmt.Fprintf(&sb, "User-agent: %s\nDisallow: /\n\n", agent)
	}
	sb.WriteString("User-agent: *\nDisallow: /\n")
	return sb.String()
}()
