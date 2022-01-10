# Refreshing Power BI Datasets using Selenium

Programmatically refresh Power BI datasets using Selenium (Opening Chrome in headless mode).


## Installation

- Clone this repository:

```bash
git clone git@github.com:truonghm/pbi_refresher.git
```

- Create a new environment and install packages from `requirements.txt`

```bash
conda create --name pbi_refresher python=3.8
conda activate pbi_refresher
cd pbi_refresher
pip install -r requirements.txt
```

- Create a `utils/config.py` file that contain username and password for logging into Power BI. See example file:

```python
pbi_config = dict(
    admin = dict(
        username = 'account1',
        password = 'pw12312312312312'
    ),
    afsdf = dict(
        username = 'account2',
        password = 'pw14t00af0234023'
    )
)

```


## Usage

### Default setting

Datasets can be added to a csv file inside `url` directory. The csv file should contain 2 columns separated by comma: id and dataset url.
Afterward, pbi_refresher can be trigger via the command line:

```bash
python pbi_refresher.py --filename=schedule1 --headless=True
```

### Specifying arguments

When the script is called WITH arguments, i.e. `--dataset_id=1,2,3,4`, only datsets with `default_frequency` set to `FALSE`, and with `id` specified in the argument will be refreshed.

```bash
python pbi_refresher.py --dataset_id=16 --pbi_config=profile1 headless=True alert=failed_only --filename=schedule1
```

In this example:
- Dataset 16 will be refreshed, but only if it has `default_frequency` set to `FALSE`.
- "Admin" credentials will be used (set in config.py).
- Run script in headless mode.
- Alert is sent only when a dataset fails to refresh.

List of arguments:

- `--dataset-id`: specifying which datasets to refresh.
- `--headless`: set to `True` to run Chrome in headless mode. Default is `True`.
- `--pbi_config`: specifying which credentials to use for logging into Power BI.
- `--alert`: takes 3 values: `{True: alerts are sent to Slack regardless of status, False: alerts are disable, Failed only: alerts are sent only when at least 1 dataset fails to refresh}`.

### Setting schedules with Task Scheduler

Using **Task Scheduler** on Windows, users can set a schedule (or multiple schedules) using the script.
It is recommended to create a batch file containing the full command and add this file to a task in Task Scheduler.
The current (default) schedule set on VM 192.168.5.28 is every hour, from 06:00 to 20:00 everyday.

## Limitations

The script uses Selenium, and as such:
- The script might break everytime Power BI changes its UI.
- Every time a task runs, Power BI is logged in. Doing this repeatedly might trigger Microsoft to block/ban/require captcha, thus causing the script to fail.
