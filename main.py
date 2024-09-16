import yaml
from playwright.sync_api import sync_playwright

from CVBB_CGYY import CVBB_CGYY

if __name__ == '__main__':
    try:
        with open('config.yaml', 'r', encoding='utf-8') as ymlfile:
            cfg = yaml.safe_load(ymlfile)
        cfg['preferred_time_list'] = [tuple(item) for item in cfg['preferred_time_list']]
        cgyy = CVBB_CGYY(cfg['student']['id'], cfg['student']['pwd'], cfg['preferred_time_list'],
                         cfg['cjy']['username'], cfg['cjy']['password'], cfg['cjy']['softid'],
                         cfg['snap_up_mode'], cfg['expected_stadium'], cfg['least_buddy_id'],
                         cfg['debug_mode'])
        with sync_playwright() as pw:
            cgyy.main(pw)

    except FileNotFoundError:
        print('Error: config file not found')
