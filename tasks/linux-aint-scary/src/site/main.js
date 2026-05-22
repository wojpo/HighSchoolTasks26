"use strict";

let emulator;
const statusBar = document.getElementById("status_bar");
const terminalContainer = document.getElementById("terminal");

function startEmulator() {
  if (emulator) {
    emulator.destroy();
    terminalContainer.replaceChildren();
  }

  emulator = new V86({
    wasm_path: "/v86/build/v86.wasm",
    memory_size: 128 * 1024 * 1024,
    vga_memory_size: 8 * 1024 * 1024,
    bios: { url: "/v86/bios/seabios.bin" },
    vga_bios: { url: "/v86/bios/vgabios.bin" },
    filesystem: {
      baseurl: "/images/alpine-rootfs-flat/",
      basefs: "/images/alpine-fs.json",
    },
    initial_state: { url: "/images/v86state.bin" },
    bzimage_initrd_from_filesystem: true,
    cmdline: "rw root=host9p rootfstype=9p rootflags=trans=virtio,cache=loose modules=virtio_pci tsc=reliable console=ttyS0",
    acpi: false,
    autostart: true,
    serial_console: {
      type: "xtermjs",
      container: terminalContainer,
      xterm_lib: Terminal,
    },
  });

  statusBar.textContent = "loading emulator";
  emulator.add_listener("download-progress", (event) => {
    if (!event.total) {
      statusBar.textContent = `loading ${event.file_name}`;
      return;
    }
    const pct = Math.floor((event.loaded / event.total) * 100);
    statusBar.textContent = `loading ${event.file_name}: ${pct}%`;
  });
  emulator.add_listener("emulator-loaded", () => {
    statusBar.textContent = "ready";
    setTimeout(() => {
      emulator.serial0_send("stty cols 120 rows 45; export COLUMNS=120 LINES=45; clear; cat /etc/joke.txt\n");
    }, 600);
  });
}

window.addEventListener("load", startEmulator);
