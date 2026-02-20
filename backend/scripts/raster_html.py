import argparse
import pathlib

from backend.app.services.render.html_raster import rasterize_html_to_png, save_png


def main():
    parser = argparse.ArgumentParser(description="Rasterize HTML to a 400-DPI A4 PNG.")
    parser.add_argument("--in", dest="inp", required=True, help="Path to HTML file")
    parser.add_argument("--out", dest="out", required=True, help="Output PNG path")
    parser.add_argument("--method", default="pdf", choices=["pdf", "screenshot"])
    parser.add_argument("--dpi", type=int, default=400)
    parser.add_argument("--selector", default=".page", help="Used only for screenshot method")
    args = parser.parse_args()

    html = pathlib.Path(args.inp).read_text(encoding="utf-8")
    png = rasterize_html_to_png(html, dpi=args.dpi, method=args.method, selector=args.selector)
    save_png(png, args.out)
    print(f"OK -> {args.out}")


if __name__ == "__main__":
    main()
