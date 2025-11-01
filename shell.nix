with import <nixpkgs> { };
pkgs.mkShell {
  name = "babbel-tux-shell";

  # Add all the libraries required by your native modules
  # You can use the following one-liner to find out which ones you need.
  # `find .venv/ -type f -name "*.so" | xargs ldd | grep "not found" | sort | uniq`
  NIX_LD_LIBRARY_PATH = lib.makeLibraryPath [
    stdenv.cc.cc # libstdc++
  ];

  NIX_LD = lib.fileContents "${stdenv.cc}/nix-support/dynamic-linker";

  packages = with pkgs; [
    uv
  ];

  shellHook = ''
    . .venv/bin/activate
  '';
}
