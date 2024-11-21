import argparse
import urllib.request
import tarfile
import gzip
import os
import sys
import tempfile
import subprocess

def download_apkindex(repo_url):
    index_url = repo_url.rstrip('/') + '/APKINDEX.tar.gz'
    tmp_dir = tempfile.mkdtemp()
    index_path = os.path.join(tmp_dir, 'APKINDEX.tar.gz')
    try:
        print(f'Downloading APKINDEX from {index_url}...')
        urllib.request.urlretrieve(index_url, index_path)
    except Exception as e:
        print(f'Error downloading APKINDEX: {e}')
        sys.exit(1)
    return index_path, tmp_dir

def extract_apkindex(index_path, tmp_dir):
    apkindex_file = os.path.join(tmp_dir, 'APKINDEX')
    try:
        with tarfile.open(index_path, 'r:gz') as tar:
            tar.extractall(path=tmp_dir)
    except Exception as e:
        print(f'Error extracting APKINDEX: {e}')
        sys.exit(1)
    return apkindex_file

def parse_apkindex(apkindex_file):
    packages = {}
    with open(apkindex_file, 'r') as f:
        content = f.read()
    entries = content.strip().split('\n\n')
    for entry in entries:
        lines = entry.strip().split('\n')
        pkg_info = {}
        for line in lines:
            if line.startswith('P:'):
                pkg_info['name'] = line[2:].strip()
            elif line.startswith('D:'):
                deps_line = line[2:].strip()
                deps = deps_line.split()
                # Clean up dependency names
                deps = [dep.split('=')[0].split('<')[0].split('>')[0].split('~')[0] for dep in deps]
                pkg_info['dependencies'] = deps
        if 'name' in pkg_info:
            name = pkg_info['name']
            packages[name] = pkg_info.get('dependencies', [])
    return packages

def build_dependency_graph(packages, package_name, max_depth):
    graph = {}
    visited = set()
    def dfs(pkg, depth):
        if depth > max_depth or pkg in visited:
            return
        visited.add(pkg)
        deps = packages.get(pkg, [])
        graph[pkg] = deps
        for dep in deps:
            dfs(dep, depth + 1)
    if package_name not in packages:
        print(f"Package '{package_name}' not found in the repository.")
        sys.exit(1)
    dfs(package_name, 1)
    return graph

def generate_dot(graph):
    dot = 'digraph dependencies {\n'
    for pkg, deps in graph.items():
        for dep in deps:
            dot += f'    "{pkg}" -> "{dep}";\n'
    dot += '}'
    return dot

def main():
    parser = argparse.ArgumentParser(description='Visualize package dependencies for Alpine Linux packages.')
    parser.add_argument('--visualizer', required=True, help='Path to the graph visualization program (e.g., dot)')
    parser.add_argument('--package', required=True, help='Name of the package to analyze')
    parser.add_argument('--depth', type=int, default=3, help='Maximum depth of dependency analysis')
    parser.add_argument('--repository', required=True, help='URL of the Alpine Linux repository')
    args = parser.parse_args()

    index_path, tmp_dir = download_apkindex(args.repository)
    apkindex_file = extract_apkindex(index_path, tmp_dir)
    packages = parse_apkindex(apkindex_file)

    graph = build_dependency_graph(packages, args.package, args.depth)
    dot_content = generate_dot(graph)

    dot_file = os.path.join(tmp_dir, 'dependencies.dot')
    with open(dot_file, 'w') as f:
        f.write(dot_content)

    output_image = os.path.join(tmp_dir, 'dependencies.png')
    try:
        subprocess.run([args.visualizer, dot_file, '-Tpng', '-o', output_image], check=True)
        print(f'Generated dependency graph image at {output_image}')
    except Exception as e:
        print(f'Error running visualization program: {e}')
        sys.exit(1)

    # Try to open the image
    try:
        if sys.platform.startswith('linux'):
            subprocess.run(['xdg-open', output_image])
        elif sys.platform == 'darwin':
            subprocess.run(['open', output_image])
        elif sys.platform.startswith('win'):
            os.startfile(output_image)
        else:

            print('Cannot determine how to open the image automatically.')
    except Exception as e:
        print(f'Error opening image: {e}')
        print('Please open the image file manually.')

    #Clean up temporary files if you wish
    #import shutil
    #shutil.rmtree(tmp_dir)

if __name__ == '__main__':
    main()
