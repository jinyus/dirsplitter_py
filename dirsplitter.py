import shutil
import typer
from pathlib import Path
import re
import traceback

APP_VERSION = '1.0.0'

app = typer.Typer(add_completion=False)


@app.command()
def version():
    typer.echo('Dirsplitter Version: %s' % APP_VERSION)


@app.command(help='Split a directory into parts of a given size')
def split(
    directory: Path = typer.Argument(
        '.', exists=True, file_okay=False, resolve_path=True),
    max: float = typer.Option(
        5.0, '-m', '--max', help='Size of each part in GB', show_default=True),
    prefix: str = typer.Option(
        '', help='Prefix for output files of the tar command. eg: myprefix.part1.tar')
):
    typer.confirm(
        f'Split "{directory}" into parts of {max} GB', abort=True, default=True)

    tracker = {1: 0}
    current_part = 1
    files_moved = 0
    failed_ops = 0

    all_files = directory.rglob('*')

    # moves ./dir/textfiles/file.txt to ./dir/part1/textfiles/file.txt

    max_size = max * 1024 * 1024 * 1024
    part_dir_regex = re.compile(str(directory.joinpath('part\d+')))
    for f in all_files:
        if f.is_dir() or part_dir_regex.findall(str(f.absolute())):
            continue

        try:
            tracker[current_part] += f.stat().st_size

            if tracker[current_part] >= max_size:
                current_part += 1
                tracker[current_part] = 0

            part_dir = directory.joinpath(f'part{current_part}')
            new_path = part_dir.joinpath(f.relative_to(directory))
            new_path.parent.mkdir(exist_ok=True, parents=True)

            f.rename(new_path)

            files_moved += 1
        except Exception as e:
            typer.echo('Failed to move file: %s' % f)
            typer.echo(e)
            print(traceback.format_exc())

            failed_ops += 1

    typer.echo('Results:')
    typer.echo(f'files moved: {files_moved}')
    typer.echo(f'failed operations: {failed_ops}')

    # print the size of each part
    for part in tracker:
        typer.echo(f'part{part}: {int(tracker[part] / 1024 / 1024)}MB')

    if prefix != '' and current_part > 0:
        typer.echo('Tar Commands:')
        if current_part == 1:
            typer.echo(
                f'tar -cf "{prefix}part1.tar" "part1"; done')
        else:
            typer.echo(
                'for n in {1..%d}; do tar -cf "%spart$n.tar" "part$n"; done' % (current_part, prefix))


@app.command(help='Reverse a split directory')
def reverse(
    directory: Path = typer.Argument(
        '.',
        exists=True,
        file_okay=False,
        resolve_path=True,
    ),

):

    folders_to_remove: set[str] = set()

    typer.confirm(f'Reverse split "{directory}"?', abort=True, default=True)
    should_delete = True

    try:
        for item in directory.iterdir():
            if item.is_dir() and re.match(r'part\d+', item.name):
                files = item.rglob('*')

                for f in files:
                    if f.is_dir():
                        continue

                    new_path = directory.joinpath(
                        f.relative_to(item))
                    f.rename(new_path)

                folders_to_remove.add(item)
    except Exception as e:
        typer.echo(f'Failed to move file')
        typer.echo(e)
        should_delete = False

    if should_delete:
        for folder in folders_to_remove:
            try:
                shutil.rmtree(folder)
            except Exception as e:
                typer.echo(f'Failed to remove folder: {folder}')
                typer.echo(e)


if __name__ == '__main__':
    app()
