{
  description = "sudosubin/freemusicarchive.py";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem
      (system:
        let
          pkgs = import nixpkgs { inherit system; };

        in
        {
          devShell = pkgs.mkShell {
            buildInputs = with pkgs; [
              (pkgs.python312.withPackages (python-pkgs: [
                python-pkgs.httpx
                python-pkgs.lxml
              ]))
            ];
          };
        }
      );
}
