import argparse
import hashlib
import logging
import os
import re
import sys


logger = logging.getLogger(__name__)


def find_first_line(lines, prefix, first_line):
    for n, content in enumerate(lines[first_line:]):
        if content.startswith(prefix):
            return True, first_line + n, content[len(prefix) :]
    return False, None, None


def find_last_line(lines, prefix, first_line):
    n_match = None
    for n, content in enumerate(lines[first_line:]):
        if content.startswith(prefix):
            n_match = n
    return (False, None) if n_match is None else (True, first_line + n_match)


def edit_guard(lines, name, linesep=os.linesep):
    ifndef_found, ifndef_n, ifndef_content = find_first_line(lines, r"#ifndef ", 0)
    assert ifndef_found, "Did not find #ifndef line. Aborting."

    define_found, define_n, define_content = find_first_line(lines, r"#define ", ifndef_n)
    assert define_found, "Did not find #define line. Aborting."

    endif_found, endif_n = find_last_line(lines, r"#endif", ifndef_n)  # Match without space OK
    assert endif_found, "Did not find #endif line. Aborting."

    assert ifndef_content.strip() == define_content.strip(), "Inconsistent guard. Aborting."

    lines[ifndef_n] = "#ifndef " + name + linesep
    lines[define_n] = "#define " + name + linesep
    lines[endif_n] = "#endif  // " + name + linesep
    return lines


def get_guardname(prefix, input, suffix, nameroot, width):
    if not os.path.isabs(nameroot):
        nameroot = os.path.normpath(os.path.join(os.getcwd(), nameroot))
    if not os.path.isabs(input):
        input = os.path.normpath(os.path.join(os.getcwd(), input))

    logger.debug("input: {}".format(input))
    logger.debug("nameroot: {}".format(nameroot))
    common = os.path.commonpath([nameroot, input])
    short_name = input[len(common) :][1:]
    logger.debug("short_name: {}".format(short_name))

    name = re.sub(r"[^a-zA-Z0-9_]", "_", short_name)
    name = re.sub(r"_+", "_", name)
    name = prefix + name + suffix
    if width > 0 and len(name) + len("#endif  // ") > width:
        full_name = prefix + short_name + suffix
        name = "HASH_" + hashlib.md5(full_name.encode(encoding="UTF-8", errors="strict")).hexdigest()
    logger.debug("name: {}".format(name))
    return name.upper()


def write_output(output_filename, lines):
    with sys.stdout if output_filename == "-" else open(output_filename, "w", encoding="utf-8") as out_fd:
        out_fd.writelines(lines)


def create_new_guard(output_filename, lines, name, linesep=os.linesep):
    new_lines = (
        [
            "#ifndef {0}{1}#define {0}{1}{1}".format(name, linesep),
        ]
        + lines
        + [
            "{1}#endif  // {0}{1}".format(name, linesep),
        ]
    )
    write_output(output_filename, new_lines)


def edit_or_create_guard(output, input, name, create, linesep=os.linesep):
    logger.debug("Processing file: {} -> {}".format(input, name))

    success = True
    with open(input, "r", encoding="utf-8") as in_fd:
        lines = in_fd.readlines()
        try:
            new_lines = edit_guard(lines, name)
        except:
            success = False
            logger.warning("Non-conforming file: {}".format(input))
    if not success:
        if create:
            logger.warning("Creating new guard: {}".format(input))
            create_new_guard(output, lines, name, linesep)
            success = True
    else:
        write_output(output, new_lines)
    return success


def recurse(searchroot, nameroot, prefix, suffix, width, create, linesep=os.linesep):
    searchroot = os.path.normpath(os.path.join(os.getcwd(), searchroot))
    assert len(searchroot) >= len(nameroot), "The DIR argument to -r must be inside the nameroot."

    success = True
    for dir, _, files in os.walk(searchroot):
        for file in files:
            input = os.path.join(dir, file)
            _, extension = os.path.splitext(input)
            if extension not in [".h", ".H", ".hpp", ".HPP"]:
                continue
            guard_name = get_guardname(prefix, input, suffix, nameroot, width)
            if not edit_or_create_guard(input, input, guard_name, create):
                success = False
    return success


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""
Replace header guard with a path-based header guard (from nameroot).
Assumes that the relevant preprocessor directives start at column 0 with no extra spacing.""",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input", type=str, default="", help="Path to input header, or hyphen (-) for stdin")
    group.add_argument(
        "-r", metavar=("DIR",), type=str, default="", help="Recursively process all .h, .H, .hpp, .HPP files from DIR"
    )

    parser.add_argument("--output", type=str, default="-", help="Path to output file, or hyphen (-) for stdout")
    parser.add_argument("--prefix", type=str, default="", help="Prefix to add to the filename guard name")
    parser.add_argument("--suffix", type=str, default="", help="Suffix to add to the filename guard name")
    parser.add_argument("--nameroot", type=str, default=None, help="Root directory for naming (default is cwd)")
    parser.add_argument("--create", action="store_true", help="Create a header guard if one does not already exist")
    parser.add_argument("--width", type=int, default=0, help="Use a hash instead of text for long lines")
    parser.add_argument("--verbose", "-v", action="count", default=0)
    parser.add_argument("--quiet", "-q", action="count", default=0)

    args = parser.parse_args()

    assert len(args.input) > 0 or len(args.r) > 0, "Use recursion, or specify an input file."
    assert not ((len(args.r) > 0) and args.create), "Creating guards recursively could be dangerous. I refuse."

    logging.basicConfig(format="%(message)s", level=logging.INFO + 10 * (args.quiet - args.verbose))

    if args.nameroot is None:
        nameroot = os.getcwd()
    else:
        nameroot = os.path.normpath(args.nameroot)
    del args.nameroot

    success = True
    if len(args.r) > 0:
        if not recurse(args.r, nameroot, args.prefix, args.suffix, args.width, args.create):
            success = False
    else:
        guard_name = get_guardname(args.prefix, args.input, args.suffix, nameroot, args.width)
        if not edit_or_create_guard(args.output, args.input, guard_name, args.create):
            success = False
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
