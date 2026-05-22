FROM docker.io/library/node:22-bookworm AS v86

RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates make python3 python3-zstandard clang lld curl default-jre-headless zstd \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.cargo/bin:${PATH}"
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y --target wasm32-unknown-unknown

WORKDIR /src
RUN git clone --depth 1 https://github.com/copy/v86.git . \
    && make build/libv86.js build/libv86.mjs build/v86.wasm build/xterm.js

FROM --platform=linux/386 docker.io/i386/alpine:3.21 AS guest

RUN apk add --no-cache busybox-static linux-virt linux-firmware-none mkinitfs \
    && mkinitfs -F 'base virtio 9p' $(cat /usr/share/kernel/virt/kernel.release)

RUN ROOT=/tinyroot \
    && mkdir -p "$ROOT"/boot "$ROOT"/bin "$ROOT"/sbin "$ROOT"/etc "$ROOT"/proc "$ROOT"/sys "$ROOT"/dev "$ROOT"/root "$ROOT"/home/ctf/.local/share/.not-trash "$ROOT"/opt/arena \
    && cp /boot/vmlinuz-virt "$ROOT"/boot/vmlinuz-virt \
    && cp /boot/initramfs-virt "$ROOT"/boot/initramfs-virt \
    && cp /bin/busybox.static "$ROOT"/bin/busybox \
    && for applet in sh mount mkdir chmod cat sleep su ps ls tr grep whoami id clear reboot; do ln -s /bin/busybox "$ROOT/bin/$applet"; done \
    && cp /bin/busybox.static "$ROOT"/sbin/init \
    && printf 'root:x:0:0:root:/root:/bin/sh\nctf:x:1000:1000:ctf:/home/ctf:/bin/sh\n' > "$ROOT"/etc/passwd \
    && printf 'root:x:0:\nctf:x:1000:\n' > "$ROOT"/etc/group \
    && printf 'hack4KrakCTF{pr0c_fd_1s_a_w1nd0w}\n' > "$ROOT"/root/flag.txt \
    && chmod 400 "$ROOT"/root/flag.txt \
    && printf '#!/bin/sh\nwhile true; do sleep 3600; done\n' > "$ROOT"/opt/arena/maintenance-daemon \
    && chmod +x "$ROOT"/opt/arena/maintenance-daemon \
    && printf 'If a door is closed, check whether somebody copied the note before locking it.\nIn Linux, a process has an environment too.\n' > "$ROOT"/home/ctf/.local/share/.not-trash/window.txt \
    && printf 'Czy ten Linux jest tak trudny?\n\nPytanie retoryczne.\n' > "$ROOT"/etc/joke.txt \
    && printf '#!/bin/sh\nmount -t proc proc /proc 2>/dev/null\nmount -t sysfs sysfs /sys 2>/dev/null\nmount -t devtmpfs devtmpfs /dev 2>/dev/null\nstty cols 120 rows 45 2>/dev/null\nexport COLUMNS=120 LINES=45\nARENA_SECRET="$(cat /root/flag.txt)" su ctf -c /opt/arena/maintenance-daemon &\nprintf "\\nLinux ain\\047t scary. User: ctf. Hint: /proc/<pid>/environ\\n\\n"\n' > "$ROOT"/etc/rcS \
    && chmod +x "$ROOT"/etc/rcS \
    && printf '::sysinit:/etc/rcS\ntty1::respawn:/bin/su ctf\nttyS0::respawn:/bin/su ctf\n::ctrlaltdel:/bin/reboot\n' > "$ROOT"/etc/inittab

FROM v86 AS assets

COPY --from=guest /tinyroot /rootfs
RUN mkdir -p /out/alpine-rootfs-flat \
    && ./tools/fs2json.py --zstd --out /out/alpine-fs.json /rootfs \
    && ./tools/copy-to-sha256.py --zstd /rootfs /out/alpine-rootfs-flat
RUN node --input-type=module - <<'EOF'
import fs from "node:fs";
import path from "node:path";
import { V86 } from "./build/libv86.mjs";

const emulator = new V86({
  bios: { url: path.resolve("bios/seabios.bin") },
  vga_bios: { url: path.resolve("bios/vgabios.bin") },
  autostart: true,
  memory_size: 128 * 1024 * 1024,
  vga_memory_size: 8 * 1024 * 1024,
  network_relay_url: "<UNUSED>",
  bzimage_initrd_from_filesystem: true,
  cmdline: "rw root=host9p rootfstype=9p rootflags=trans=virtio,cache=loose modules=virtio_pci tsc=reliable console=ttyS0",
  filesystem: {
    baseurl: path.resolve("/out/alpine-rootfs-flat"),
    basefs: path.resolve("/out/alpine-fs.json"),
  },
});

let serial = "";
let done = false;
emulator.add_listener("serial0-output-byte", byte => {
  serial += String.fromCharCode(byte);
  if (!done && serial.includes("Linux ain't scary")) {
    done = true;
    setTimeout(async () => {
      const state = await emulator.save_state();
      fs.writeFileSync("/out/v86state.bin", new Uint8Array(state));
      emulator.destroy();
      process.exit(0);
    }, 1000);
  }
});

setTimeout(() => {
  console.error(serial.slice(-4000));
  process.exit(1);
}, 120000);
EOF

FROM docker.io/library/nginx:1.28-alpine

COPY src/nginx.conf /etc/nginx/conf.d/default.conf
COPY src/site/ /usr/share/nginx/html/
COPY --from=v86 /src/build/libv86.js /usr/share/nginx/html/v86/build/libv86.js
COPY --from=v86 /src/build/v86.wasm /usr/share/nginx/html/v86/build/v86.wasm
COPY --from=v86 /src/build/xterm.js /usr/share/nginx/html/v86/build/xterm.js
COPY --from=v86 /src/build/xterm.css /usr/share/nginx/html/v86/build/xterm.css
COPY --from=v86 /src/bios/seabios.bin /usr/share/nginx/html/v86/bios/seabios.bin
COPY --from=v86 /src/bios/vgabios.bin /usr/share/nginx/html/v86/bios/vgabios.bin
COPY --from=assets /out/alpine-fs.json /usr/share/nginx/html/images/alpine-fs.json
COPY --from=assets /out/alpine-rootfs-flat /usr/share/nginx/html/images/alpine-rootfs-flat
COPY --from=assets /out/v86state.bin /usr/share/nginx/html/images/v86state.bin

EXPOSE 8080
