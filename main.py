import yaml
from playwright.sync_api import sync_playwright

from CVBB_CGYY import CVBB_CGYY

if __name__ == '__main__':
    try:
        with open('config.yaml', 'r', encoding='utf-8') as ymlfile:
            cfg = yaml.safe_load(ymlfile)
        cfg['preferred_time_list'] = [tuple(item) for item in cfg['preferred_time_list']]
        cgyy = CVBB_CGYY(stu_info=cfg['student'], prior_list=cfg['preferred_time_list'], verify_info=cfg['cjy'],
                         ip_info=cfg['ip'], scheduled_mode=cfg['scheduled_mode'], stadium=cfg['expected_stadium'],
                         buddy=cfg['buddy'], debug_mode=cfg['debug_mode'], timer=cfg['timer'])
        with sync_playwright() as pw:
            cgyy.main(pw)

    except FileNotFoundError:
        print('Error: config file not found')
