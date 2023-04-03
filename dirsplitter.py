import shutil
import click
from pathlib import Path
import re
import traceback

APP_VERSION = '1.0.0'


@click.group()
def cli():
    pass


@click.command()
def version():
    click.echo('Dirsplitter Version: %s' % APP_VERSION)


@click.command()
@click.argument(
    'directory', default='.',
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
)
@click.option('-m', '--max', default=5.0, help='Size of each part in GB', type=click.FLOAT, show_default=True)
@click.option('-p', '--prefix', default='', help='Prefix for output files of the tar command. eg: myprefix.part1.tar')
def split(directory: Path, max: float, prefix: str):
    click.confirm(
        f'Split "{directory}" into parts of {max} GB', abort=True, default=True)

    tracker = {1: 0}
    current_part = 1
    files_moved = 0
    failed_ops = 0

    all_files = Path(directory).rglob('*')

    # moves ./dir/textfiles/file.txt to ./dir/part1/textfiles/file.txt

    max_size = max * 1024 * 1024 * 1024
    part_dir_regex = re.compile(str(Path(directory).joinpath('part\d+')))
    for f in all_files:
        if f.is_dir() or part_dir_regex.findall(str(f.absolute())):
            continue

        try:
            tracker[current_part] += f.stat().st_size

            if tracker[current_part] >= max_size:
                current_part += 1
                tracker[current_part] = 0

            part_dir = Path(directory).joinpath(f'part{current_part}')
            new_path = part_dir.joinpath(f.relative_to(directory))
            new_path.parent.mkdir(exist_ok=True, parents=True)

            f.rename(new_path)

            files_moved += 1
        except Exception as e:
            click.echo('Failed to move file: %s' % f)
            click.echo(e)
            print(traceback.format_exc())

            failed_ops += 1

    click.echo('Results:')
    click.echo(f'files moved: {files_moved}')
    click.echo(f'failed operations: {failed_ops}')

    # print the size of each part
    for part in tracker:
        click.echo(f'part{part}: {int(tracker[part] / 1024 / 1024)}MB')

    if prefix != '' and current_part > 0:
        click.echo('Tar Commands:')
        if current_part == 1:
            click.echo(
                f'tar -cf "{prefix}part1.tar" "part1"; done')
        else:
            click.echo(
                f'for n in 1..{current_part}; do tar -cf "{prefix}part$n.tar" "part$n"; done')


@click.command()
@click.argument(
    'directory', default='.',
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
)
def reverse(directory: Path):
    # moves ./dir/part1/textfiles/file.txt to ./dir/textfiles/file.txt
    folders_to_remove: set[str] = set()

    click.confirm(f'Reverse split "{directory}"?', abort=True, default=True)
    should_delete = True

    try:
        for item in Path(directory).iterdir():
            if item.is_dir() and re.match(r'part\d+', item.name):
                files = item.rglob('*')

                for f in files:
                    if f.is_dir():
                        continue

                    new_path = Path(directory).joinpath(f.relative_to(item))
                    f.rename(new_path)

                folders_to_remove.add(item)
    except Exception as e:
        click.echo(f'Failed to move file')
        click.echo(e)
        should_delete = False

    if should_delete:
        for folder in folders_to_remove:
            try:
                shutil.rmtree(folder)
            except Exception as e:
                click.echo(f'Failed to remove folder: {folder}')
                click.echo(e)


cli.add_command(version)
cli.add_command(split)
cli.add_command(reverse)


if __name__ == '__main__':
    cli()
