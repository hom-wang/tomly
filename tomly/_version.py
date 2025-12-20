__version__ = "0.1.1"
__repository__ = r"https://github.com/hom-wang/tomly.git"


def extract_metadata(project_toml: str) -> dict:
    project_toml: Path = Path(project_toml)
    if not project_toml.exists():
        return {}

    proj = toml.load(project_toml).get("project", {})
    author = proj.get("authors", [{}])[0]
    return {
        "__version__": proj.get("version", ""),
        "__author__": author.get("name", ""),
        "__email__": author.get("email", ""),
        "__license__": proj.get("license", ""),
        "__description__": proj.get("description", ""),
    }


def update_metadata(target_file: str, metadata: dict) -> bool:
    target_file: Path = Path(target_file)
    if not target_file.exists():
        return False

    with open(target_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if len(line) > 2 and line[:2] == "__"]

    content = target_file.read_text(encoding="utf-8")
    for line in lines:
        for k, v in metadata.items():
            if k in line:
                content = content.replace(line, f'{k} = "{v}"')

    with open(target_file, "w", encoding="utf-8") as f:
        f.write(content)

    return True


if __name__ == "__main__":
    from pathlib import Path

    import rtoml as toml

    project_toml = Path(__file__).parents[1] / "pyproject.toml"
    metadata_file = Path(__file__).parent / "_version.py"

    metadata = extract_metadata(project_toml)
    rtn = update_metadata(metadata_file, metadata)
    exit(0 if rtn else 1)
