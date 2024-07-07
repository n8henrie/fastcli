{
  description = "Flake for https://github.com/n8henrie/fastcli";

  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
  outputs =
    { self, nixpkgs }:
    let
      systems = [
        "aarch64-darwin"
        "x86_64-darwin"
        "x86_64-linux"
        "aarch64-linux"
      ];
      eachSystem =
        with nixpkgs.lib;
        f: foldAttrs mergeAttrs { } (map (s: mapAttrs (_: v: { ${s} = v; }) (f s)) systems);
    in
    eachSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pname = "fastcli";
      in
      {
        packages = {
          default = pkgs.python312.withPackages (_: [ self.packages.${system}.${pname} ]);
          ${pname} = pkgs.callPackage (
            { lib, python3Packages }:
            python3Packages.buildPythonPackage {
              inherit pname;
              version = builtins.elemAt (lib.splitString "\"" (
                lib.findSingle (val: builtins.match "^__version__ = \".*\"$" val != null) (abort "none")
                  (abort "multiple")
                  (lib.splitString "\n" (builtins.readFile ./${pname}/__init__.py))
              )) 1;
              src = lib.cleanSource ./.;
              pyproject = true;
              nativeBuildInputs = with python3Packages; [ pythonRelaxDepsHook ];
              build-system = [ python3Packages.setuptools-scm ];
              dependencies = with python3Packages; [ aiohttp ];
              pythonRelaxDeps = [ "aiohttp" ];
            }
          ) { };
        };

        devShells.${system}.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python38
            python39
            python310
            python311
            (python312.withPackages (
              ps:
              propagatedBuildInputs
              ++ (with ps; [
                mypy
                pytest
                tox
              ])
            ))
          ];
        };
      }
    );
}
