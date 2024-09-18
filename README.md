# CVBB_CGYY

抢场！抢场！抢场！

这个口号从高中延续下来了……如今，自动化脚本终于实现了。

## Prerequisites

### Verification

要使用这个脚本，首先请到[超级鹰](https://www.chaojiying.com/)平台注册并充值，然后获取你的账户、密码的md5值、软件id。

### Requirements

克隆项目后，在根目录下运行：

```commandline
pip3 install -r ./requirements.txt
playwright install
```

### Info

打开 `example/` 文件夹，复制里面的 `config.yaml` 到项目根目录下，修改里面的内容，填上必要的信息。

### Proxy

如果你的 IP 和我一样被学校封了，可以使用代理模式，详见 `config.yaml` 里的注释。

注：不建议使用代理模式，相比正常模式运行慢3倍（当然依旧可观）。如果你的 IP 被封了，可以手动修改本机设置，将 DHCP 改为静态并更换 IP。

## Run

```commandline
python3 main.py
```

请注意，如果要挂机抢场，需要保证电脑整晚一直运行。Windows 10+
可以使用 [PowerToys Awake](https://learn.microsoft.com/zh-cn/windows/powertoys/awake)。

暂不支持自动支付，所以订一个 7 点的闹钟，以确保你能在 10 分钟内及时支付！！！

## Thanks

- [max-vegetable/BUAA_CGYY](https://github.com/max-vegetable/BUAA_CGYY)：前辈的劳动成果，后人只是在这一思想上做了改进。
- [HawkQ/buaa-gw](https://github.com/HawkQ/buaa-gw)：本项目中自动登录网络脚本的直接来源。
- [huxiaofan1223/jxnu_srun](https://github.com/huxiaofan1223/jxnu_srun)
  ：自动登录网络的根本来源，详见[博主原文分析](https://blog.csdn.net/qq_41797946/article/details/89417722)

## Buy us a cup of coffee!

![xxk](sponsored.jpg)