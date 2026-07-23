{
  pkgs,
  lib,
  config,
  ...
}:
{
  packages = with pkgs; [
    zlib
    stdenv.cc.cc.lib
    ffmpeg 
  ];
  # https://devenv.sh/languages/
  languages.python = {
    enable = true;
    uv.enable = true;
  };

  languages.javascript = {
    enable = true;
    pnpm = {
      enable = true;
      install.enable = true;
    };
  };
}
