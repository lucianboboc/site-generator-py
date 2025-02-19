from textnode import TextNode, TextType
from pathlib import Path
import shutil
from funcs import copy_directory_recursive, generate_pages_recursive


def main():
    project_root = Path(__file__).parent.parent

    public_dir = project_root / "public"
    static_dir = project_root / "static"

    # remove before copying
    if public_dir.exists():
        shutil.rmtree(public_dir)

    copy_directory_recursive(static_dir, public_dir)

    from_path = project_root / "content"
    template_path = project_root / "template.html"
    dest_path = project_root / "public"

    generate_pages_recursive(from_path, template_path, dest_path)


if __name__ == "__main__":
    main()
