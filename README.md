# cirrus-ci-tools

_**Cirrus-ci-tools**_ is a tool to interact with [Cirrus CI](https://cirrus-ci.org/).

For instances, it can be used to trigger a [Cirrus CI](https://cirrus-ci.org/) build task.

## Usage
```shell
$ ./trigger-cirrus-ci.py --help
usage: trigger-cirrus-ci.py [-h] -t TOKEN -r REPOSITORY -b BRANCH [-c CONFIG] [-T TIMEOUT] [-i INTERVAL]

options:
  -h, --help            show this help message and exit
  -t TOKEN, --token TOKEN
                        Cirrus-CI TOKEN
  -r REPOSITORY, --repository REPOSITORY
                        GitHub repository
  -b BRANCH, --branch BRANCH
                        The branch of the repository
  -c CONFIG, --config CONFIG
                        The configuration YAML
  -T TIMEOUT, --timeout TIMEOUT
                        Timeout (in minutes)
  -i INTERVAL, --interval INTERVAL
                        Sleep interval (in seconds)

```

## Examples

* Integration with GitHub Actions.

```yaml
cirrus-ci-build:
  name: Cirrus CI Build
  runs-on: ubuntu-latest
  # Set up the environment.
  # https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment
  environment: CIRRUS-CI
  steps:
    - name: Checkout
      uses: actions/checkout@v3
      with:
        repository: ${{ github.repository }}
        ref: 'cirrus'
        submodules: true

    - name: Build and Download
      run: |
        trigger='.github/cirrus-ci-tools/src/trigger-cirrus-ci.py'
        config='.github/cirrus-ci/build_toolchain.yml'

        urls="$(python3 "${trigger}" --token ${{ secrets.CIRRUS_CI_TOKEN }} --repository ${{ github.repository }} \
          --branch master --config "${config}" --timeout 240)"

        while read -r url; do
          echo "The artifact url: ${url}"
          curl -L ${url} -o binary.zip
          unzip binary.zip
        done <<<"${urls}"
```
