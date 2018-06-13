# -*- coding: utf-8 -*-
#
# Copyright 2018 - Swiss Data Science Center (SDSC)
# A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
# Eidgenössische Technische Hochschule Zürich (ETHZ).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Show status of data files created in the repository.

Inspecting a repository
~~~~~~~~~~~~~~~~~~~~~~~

Displays paths of outputs which were generated from newer inputs files
and paths of files that have been used in diverent versions.

The first paths are what need to be recreated by running ``renku update``.
See more in section about :ref:`renku update <cli-update>`.

The paths mentioned in the output are made relative to the current directory
if you are working in a subdirectory (this is on purpose, to help
cutting and pasting to other commands). They also contain first 8 characters
of the corresponding commit identifier after the ``#`` (hash). If the file was
imported from another repository, the short name of is shown together with the
filename before ``@``.
"""

import click

from ._ascii import _format_sha1
from ._client import pass_local_client
from ._git import with_git
from ._graph import Graph


@click.command()
@click.option(
    '--revision',
    default='HEAD',
    help='Display status as it was in the given revision'
)
@click.argument('path', type=click.Path(exists=True, dir_okay=False), nargs=-1)
@pass_local_client
@click.pass_context
@with_git(commit=False)
def status(ctx, client, revision, path):
    """Show a status of the repository."""
    graph = Graph(client)
    # TODO filter only paths = {graph.normalize_path(p) for p in path}
    status = graph.build_status(revision=revision)

    click.echo('On branch {0}'.format(client.git.active_branch))
    if status['outdated']:
        click.echo('Files generated from newer inputs:')
        click.echo('  (use "renku log [<file>...]" to see the full lineage)')
        click.echo(
            '  (use "renku update [<file>...]" to '
            'generate the file from its latest inputs)'
        )
        click.echo()

        for filepath, files in status['outdated'].items():
            outdated = (
                ', '.join(
                    '{0}#{1}'.format(
                        click.
                        style(graph._format_path(p), fg='blue', bold=True),
                        _format_sha1(graph, (c, p)),
                    ) for c, p in stts
                    if not p.startswith('.renku/workflow/') and
                    p not in status['outdated']
                ) for stts in files
            )

            click.echo(
                '\t{0}: {1}'.format(
                    click.style(
                        graph._format_path(filepath), fg='red', bold=True
                    ), ', '.join(outdated)
                )
            )

        click.echo()

    else:
        click.secho(
            'All files were generated from the latest inputs.', fg='green'
        )

    if status['multiple-versions']:
        click.echo('Input files used in different versions:')
        click.echo(
            '  (use "renku log --revision <sha1> <file>" to see a lineage '
            'for the given revision)'
        )
        click.echo()

        for filepath, files in status['multiple-versions'].items():
            commits = (_format_sha1(graph, key) for key in files)
            click.echo(
                '\t{0}: {1}'.format(
                    click.style(
                        graph._format_path(filepath), fg='blue', bold=True
                    ), ', '.join(commits)
                )
            )

        click.echo()

    ctx.exit(1 if status['outdated'] else 0)
