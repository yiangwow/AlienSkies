#!/usr/bin/env python3
"""
Send a Python command/file to the running Unreal Editor via Remote Execution.

Usage:
    python3 run.py "import unreal; print(unreal.SystemLibrary.get_engine_version())"
    python3 run.py --file iterate_sky.py
"""

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import remote_execution as remote


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', nargs='?', help='Python statement to run')
    parser.add_argument('--file', help='Path to a .py file to execute (resolved relative to Scripts/)')
    parser.add_argument('--timeout', type=float, default=10.0)
    args = parser.parse_args()

    if args.file:
        script_path = args.file
        if not os.path.isabs(script_path):
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script_path)
        # MODE_EXEC_FILE expects the editor to load it by path
        code = script_path
        exec_mode = remote.MODE_EXEC_FILE
    elif args.command:
        code = args.command
        exec_mode = remote.MODE_EXEC_STATEMENT
    else:
        parser.error('Provide a command or --file')

    config = remote.RemoteExecutionConfig()
    rex = remote.RemoteExecution(config)
    rex.start()

    # Discover the editor
    deadline = time.time() + args.timeout
    while not rex.remote_nodes and time.time() < deadline:
        time.sleep(0.1)

    if not rex.remote_nodes:
        print('ERROR: no Unreal Editor found on the network. Is Remote Execution enabled?', file=sys.stderr)
        rex.stop()
        sys.exit(2)

    node_id = rex.remote_nodes[0]['node_id']
    rex.open_command_connection(node_id)
    try:
        result = rex.run_command(
            code,
            exec_mode=exec_mode,
        )
        # Print output
        for entry in result.get('output', []):
            print(f"[{entry['type']}] {entry['output']}", end='')
        if result.get('success'):
            print('\n--- OK ---')
        else:
            print(f"\n--- FAILED: {result.get('result')} ---")
            sys.exit(1)
    finally:
        rex.close_command_connection()
        rex.stop()


if __name__ == '__main__':
    main()
