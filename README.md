# Refreshing Power BI Datasets using Selenium

Programmatically refresh Power BI datasets using Selenium (Opening Chrome in headless mode).


## Installation

- Clone this repository:

```bash
git clone git@gitlab.id.vin:truong.hoang/pbi_refresher.git
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
    anh_cuong = dict(
        username = 'account2',
        password = 'pw14t00af0234023'
    )
)

```


## Usage

### Default setting

Datasets can be added at the [following google sheet](https://docs.google.com/spreadsheets/d/1A2YQOSySyg0Ajhd2tVfqNIs1uqqO4wg8zwzvxXIUjnw/edit#gid=0).

| id  | report_name | dataset_url                                                           | default_frequency | active_status |
| --- | ----------- | --------------------------------------------------------------------- | ----------------- | :-----------: |
| 1   | Report 1    | https://app.powerbi.com/groups/workspace_1/datasets/dataset_1/details | TRUE              |       A       |
| 2   | Report 2    | https://app.powerbi.com/groups/workspace_2/datasets/dataset_2/details | TRUE              |       A       |
| 3   | Report 3    | https://app.powerbi.com/groups/workspace_3/datasets/dataset_3/details | TRUE              |       I       |

When the script is called without arguments, datasets with `default_frequency` set to `TRUE` will be refreshed.

```bash
python pbi_refresher.py
```

### Specifying arguments

When the script is called WITH arguments, i.e. `--dataset_id=1,2,3,4`, only datsets with `default_frequency` set to `FALSE`, and with `id` specified in the argument will be refreshed.

```bash
python pbi_refresher.py --dataset_id=16 --pbi_config=admin headless=True alert=failed_only
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