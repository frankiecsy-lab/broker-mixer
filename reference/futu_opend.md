# Futu OpenAPI 文档 (JavaScript)


---

# 介绍

## 概述
量化接口，为您的程序化交易，提供丰富的行情和交易接口，满足每一位开发者的量化投资需求，助力您的宽客梦想。

牛牛用户可以 [点击这里](https://www.futunn.com/OpenAPI)了解更多。

Futu API 由 OpenD 和API SDK组成：
* OpenD 是 Futu API 的网关程序，运行于您的本地电脑或云端服务器，负责中转协议请求到富途后台，并将处理后的数据返回。
* API SDK是富途为主流的编程语言（Python、Java、C#、C++、JavaScript）封装的SDK，以方便您调用，降低策略开发难度。如果您希望使用的语言没有在上述之列，您仍可自行对接裸协议，完成策略开发。

下面的框架图和时序图，帮助您更好地了解 Futu API。

 ![openapi-frame](../img/nnopenapi-frame.png)

 ![openapi-interactive](../img/nnopenapi-interactive.png)

初次接触 Futu API，您需要进行如下两步操作：

第一步，在本地或云端安装并启动一个网关程序 [OpenD](../quick/opend-base.md)。

OpenD 以自定义 TCP 协议的方式对外暴露接口，负责中转协议请求到富途服务器，并将处理后的数据返回，该协议接口与编程语言无关。

第二步，下载 Futu API，完成 [环境搭建](../quick/env.md)，以便快速调用。

为方便您的使用，富途对主流的编程语言，封装了相应的 API SDK（以下简称 Futu API）。


## 账号
Futu API 涉及 2 类账号，分别是 **平台账号** 和 **综合账户**。

### 平台账号

平台账号是您在富途的用户 ID（牛牛号），此账号体系适用于富途牛牛 APP、Futu API。  
您可以使用平台账号（牛牛号）和登录密码，登录 OpenD 并获取行情。

### 综合账户
综合账户支持以多种货币在同一个账户内交易不同市场品类（港股、美股、A股通、基金）。您可以通过一个账户进行全市场交易，不需要再管理多个账户。  
综合账户包括综合账户 - 证券，综合账户 - 期货，综合账户 - 加密货币等业务账户：  
* 综合账户 - 证券，用于交易全市场的股票、ETFs、期权等证券类产品。  
* 综合账户 - 期货，用于交易全市场的期货产品，目前支持香港市场期货、美国市场 CME Group 期货、新加坡市场期货、日本市场期货。
* 综合账户 - 加密货币，用于交易加密货币币对，目前支持 FUTU HK、moomoo US、moomoo SG 券商。


## 功能
Futu API 的功能主要有两部分：行情和交易。

### 行情功能

#### 行情数据品类

支持香港、美国、A 股、新加坡、马来西亚、日本市场的行情数据，涉及的品类包括股票、指数、期权、期货等，具体支持的品种见下表。  
获取行情数据需要相关权限，如需了解行情权限的获取方式以及限制规则，请 [点击这里](./authority.md#2867)。

<table>
    <tr>
        <th>市场</th>
        <th>品种</th>
        <th>牛牛用户</th>
    </tr>
    <tr>
        <td rowspan="5">香港市场</td>
	    <td>股票、ETFs、窝轮、牛熊、界内证</td>
	    <td align="center">✓</td>
    </tr>
    <tr>
        <td>期权</td>
        <td align="center">✓</td>
    </tr>
    <tr>
	    <td>期货</td>
        <td align="center">✓</td>
    </tr>
    <tr>
	    <td>指数</td>
        <td align="center">✓</td>
    </tr>
    <tr>
	    <td>板块</td>
        <td align="center">✓</td>
    </tr>
    <tr>
        <td rowspan="6">美国市场</td>
	    <td>股票、ETFs (含纽交所、美交所、纳斯达克上市的股票、ETFs)</td>
	    <td align="center">✓</td>
    </tr>
    <tr>
	    <td>OTC 股票</td>
        <td align="center">X</td>
    </tr>
    <tr>
        <td>期权  (含普通股票期权、指数期权)</td>
        <td align="center">✓</td>
    </tr>
    <tr>
	    <td>期货</td>
        <td align="center">✓</td>
    </tr>
    <tr>
	    <td>指数</td>
        <td align="center">X</td>
    </tr>
    <tr>
	    <td>板块</td>
        <td align="center">✓</td>
    </tr>
    <tr>
        <td rowspan="3">A 股市场</td>
	    <td>股票、ETFs</td>
        <td align="center">✓</td>
    </tr>
    <tr>
	    <td>指数</td>
        <td align="center">✓</td>
    </tr>
    <tr>
	    <td>板块</td>
        <td align="center">✓</td>
    </tr>
    <tr>
        <td rowspan="2">新加坡市场</td>
	    <td>股票、ETFs、REITs、DLCs、结构性窝轮</td>
        <td align="center">✓</td>
    </tr>
    <tr>
	    <td>期货</td>
        <td align="center">X</td>
    </tr>
    <tr>
        <td rowspan="1">马来西亚市场</td>
        <td>股票、ETFs、窝轮、REITs</td>
        <td align="center">✓</td>
    </tr>
    <tr>
        <td rowspan="2">日本市场</td>
        <td>股票、ETFs</td>
        <td align="center">✓</td>
    </tr>
    <tr>
	    <td>期货</td>
        <td align="center">X</td>
    </tr>
    <tr>
        <td rowspan="1">澳大利亚市场</td>
        <td>股票、ETFs</td>
        <td align="center">X</td>
    </tr>
    <tr>
        <td rowspan="1">环球市场</td>
        <td>外汇</td>
        <td align="center">X</td>
    </tr>
    <tr>
        <td rowspan="1">加密货币市场</td>
        <td>加密货币</td>
        <td align="center">✓</td>
    </tr>
</table>

#### 行情数据获取方式

* 订阅并接收实时报价、实时 K 线、实时逐笔、实时摆盘等数据推送
* 拉取最新市场快照，历史 K 线等

### 交易功能

#### 交易能力
支持香港、美国、A 股、新加坡、日本、马来西亚等多个市场的交易能力，涉及的品类包括股票、期权、期货等，具体见下表：

<table>
    <tr>
        <th rowspan="2">市场</th>
        <th rowspan="2">品种</th>
        <th rowspan="2">模拟交易</th>
        <th colspan="7">真实交易</th>
    </tr>
    <tr>
        <th>FUTU HK</th>
        <th>Moomoo US</th>
        <th>Moomoo SG</th>
        <th>Moomoo AU</th>
        <th>Moomoo MY</th>
        <th>Moomoo CA</th>
        <th>Moomoo JP</th>
    </tr>
    <tr>
        <td rowspan="3">香港市场</td>
	    <td>股票、ETFs、窝轮、牛熊、界内证</td>
	    <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
	    <td>期权 (含指数期权，需使用期货账户交易)</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
	    <td>期货</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
        <td rowspan="3">美国市场</td>
	    <td>股票、ETFs</td>
	    <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
    </tr>
    <tr>
        <td>期权</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
    </tr>
    <tr>
	    <td>期货</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
        <td rowspan="2">A 股市场</td>
	    <td>A 股通股票</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
	    <td>非 A 股通股票</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
        <td rowspan="2">新加坡市场</td>
	    <td>股票、ETFs、结构性窝轮、REITs、DLCs</td>
        <td align="center">X</td>
        <td align="center">✓ (FUTU HK暂不支持交易结构性窝轮)</td>
        <td align="center">X</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
	    <td>期货</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
	    <td rowspan="2">日本市场</td>
        <td>股票、ETFs、REITs</td>
        <td align="center">X</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">✓</td>
    </tr>
    <tr>
        <td>期货</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
	    <td rowspan="1">马来西亚市场</td>
        <td>股票、ETFs</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
	    <td rowspan="1">澳大利亚市场</td>
        <td>股票、ETFs</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
	    <td rowspan="1">加拿大市场</td>
        <td>股票</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
	    <td rowspan="1">加密货币市场 (需开通加密货币交易权限)</td>
        <td>加密货币</td>
        <td align="center">X</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
</table>

#### 交易方式
真实交易和模拟交易使用同一套交易接口。


## 特点

1. 全平台多语言：
* OpenD 支持 Windows、MacOS、CentOS、Ubuntu
* Futu API 支持 Python、Java、C#、C++、JavaScript 等主流语言
2. 稳定极速免费：
* 稳定的技术架构，直连交易所一触即达
* 下单最快只需 0.0014 s
* 通过 Futu API 交易无附加收费
3. 丰富的投资品类：
* 支持美国、香港、新加坡、日本、马来西亚、加密货币等多个市场的实时行情、实盘交易及部分品类模拟交易
4. 专业的机构服务：
* 定制化的行情交易解决方案

---

# 权限与额度

## 登录
### 登录账号

Futu API 现已全面放开登录限制，进一步优化开发体验。无需开户限制，您可使用富途牛牛号（或注册时使用的手机号/邮箱）登录 OpenD。

### 合规确认

首次登录成功后，您需要完成问卷评估与协议确认，才能继续使用 Futu API。牛牛用户请 [点击这里](https://www.futunn.com/about/api-disclaimer)。


## 行情数据
行情数据的限制主要体现在以下几方面：
* 行情权限 —— 获取相关行情数据的权限
* 接口限频 —— 调用行情接口的频率限制
* 订阅额度 —— 同时订阅的实时行情的数量
* 历史 K 线额度 —— 每 7 天最多可拉取多少个标的的历史 K 线

### 行情权限

通过 Futu API 获取行情数据，需要相应的行情权限，Futu API 的行情权限跟 APP 的行情权限不完全一样，不同的权限等级对应不同的时延、摆盘档数以及接口使用权限。

部分品种行情，需要购买行情卡后方可获取，具体获取方式见下表。

<table>
    <tr>
        <th>市场</th>
        <th>标的类别</th>
        <th>获取方式</th>
    </tr>
    <tr>
        <td rowspan="5">香港市场</td>
	    <td>证券类产品（含股票、ETFs、窝轮、牛熊、界内证）</td>
	    <td  rowspan="3" align="left">• 境内认证客户：免费获取 LV2 行情。如需获得 SF 权限，请购买 <a href="https://qtcard.futunn.com/intro/sf?type=10&is_support_buy=1&clientlang=0" target="_blank">港股高级全盘行情</a>  <br>• 国际客户：免费获取 LV1 行情。如需获得 LV2 权限，请购买 <a href="https://qtcard.futunn.com/intro/hklv2?type=1&is_support_buy=1&clientlang=0" target="_blank">港股 LV2 高级行情</a> 。如需获得 SF 权限，请购买 <a href="https://qtcard.futunn.com/intro/sf?type=10&is_support_buy=1&clientlang=0" target="_blank">港股高级全盘行情</a></td>
    </tr>
    <tr>
	    <td>指数</td>
    </tr>
    <tr>
	    <td>板块</td>
    </tr>
    <tr>
        <td>期权</td>
	    <td  rowspan="2" align="left">• 境内认证客户：推广期免费获取 LV2 行情  <br>• 国际客户：免费获取 LV1 行情，如需获得 LV2 权限，请购买 <a href="https://qtcard.futunn.com/intro/hk-derivativeslv2?type=8&clientlang=0&is_support_buy=1" target="_blank">港股期权期货 LV2 高级行情</a></td>
    </tr>
    <tr>
	    <td>期货</td>
    </tr>
    <tr>
        <td rowspan="6">美国市场</td>
	    <td>证券类产品（含纽交所、美交所、纳斯达克上市的股票、ETFs）</td>
	    <td  rowspan="2" align="left">• 推广期<b>免费获取</b> LV3 行情（Nasdaq Baisc + Nasdaq TotalView + NYSE Arcabook） <br>• NYSE Arcabook 深度摆盘获取需先完成 <a href="https://qtcard.futunn.com/question/us?lang=zh-cn" target="_blank">非专业用户评估问卷 </a></td>
    </tr>
    <tr>
	    <td>板块</td>
    </tr>
    <tr>
	    <td>OTC 股票</td>
        <td  align="left">暂不支持获取</td>
    </tr>
    <tr>
        <td>期权（含普通股票期权、指数期权）</td>
	    <td  align="left">• 达到门槛  (门槛要求为：总资产大于20000港元) 的客户：免费获得 LV1 权限。 <br>• 未达到门槛  (门槛要求为：总资产大于20000港元) 的客户：请购买 <a href="https://qtcardfthk.futufin.com/intro/api-usoption-realtime?type=16&is_support_buy=1&clientlang=0" target="_blank">OPRA 期权 LV1 实时行情</a> 获得 LV1 权限。</td>
    </tr>
    <tr>
	    <td>期货</td>
        <td  align="left">• 已开通期货账户：<br> 如需获取 CME Group 行情  (包含 CME, CBOT, NYMEX, COMEX 行情) ，请购买 <a href="https://qtcardfthk.futufin.com/intro/cme?type=30&clientlang=0&is_support_buy=1" target="_blank">CME Group 期货 LV2</a> <br>如需获取 CME 行情，请购买 <a href="	https://qtcardfthk.futufin.com/intro/cme?type=31&clientlang=0&is_support_buy=1" target="_blank">CME 期货 LV2</a> <br>如需获取 CBOT 行情，请购买 <a href="https://qtcardfthk.futufin.com/intro/cme?type=32&clientlang=0&is_support_buy=1" target="_blank">CBOT 期货 LV2</a> <br>如需获取 NYMEX 行情，请购买 <a href="	https://qtcardfthk.futufin.com/intro/cme?type=33&clientlang=0&is_support_buy=1" target="_blank">NYMEX 期货 LV2</a> <br>如需获取 COMEX 行情，请购买 <a href="	https://qtcardfthk.futufin.com/intro/cme?type=34&clientlang=0&is_support_buy=1" target="_blank">COMEX 期货 LV2</a>   <br> <br>• 未开通期货账户：不支持获取</td>
    </tr>
    <tr>
	    <td>指数</td>
        <td  align="left">暂不支持获取</td>
    </tr>
    <tr>
        <td rowspan="3">A 股市场</td>
	    <td>证券类产品（含股票、ETFs）</td>
	    <td  rowspan="3">• 境内认证客户：免费获取 LV1 行情<br>• 国际客户：暂不支持</td>
    </tr>
    <tr>
	    <td>指数</td>
    </tr>
    <tr>
	    <td>板块</td>
    </tr>
    <tr>
        <td rowspan="2">新加坡市场</td>
	    <td>证券类产品（含股票、ETFs、REITs）</td>
	    <td  align="left">暂不支持获取</td>  
    </tr> 
    </tr>
    <tr>
	    <td>期货</td>
	    <td  align="left">暂不支持获取</td>
    </tr>
    <tr>
        <td rowspan="1">马来西亚市场</td>
	    <td>证券类产品（含股票、ETFs、窝轮、REITs）</td>
	    <td  align="left">暂不支持获取</td>  
    </tr>
    <tr>
        <td rowspan="2">日本市场</td>
	    <td>证券类产品（含股票、ETFs）</td>
	    <td  align="left">暂不支持获取</td>  
    </tr>
    <tr>
	    <td>期货</td>
	    <td  align="left">暂不支持获取</td>
    </tr>
    <tr>
        <td rowspan="1">加密货币市场</td>
	    <td>加密货币</td>
	    <td  align="left">推广期内免费获取，支持获取主流币种及现货币对行情</td>
    </tr>
</table>

:::tip 提示

上述表格，境内认证客户和国际客户，以 OpenD 登录的 IP 地址作为区分依据。   
平台对 API 行情产品的订阅方式、授权范围及收费标准保留调整权利。如有变更,以届时公告及产品页面展示为准。请您关注公告并及时完成订阅。

:::

### 接口限频
为保护服务器，防止恶意攻击，所有需要向富途服务器发送请求的接口，都会有频率限制。  
每个接口的限频规则会有不同，具体请参见每个接口页面下面的 `接口限制`。

举例：  
[快照](../quote/get-market-snapshot.md) 接口的限频规则是：每 30 秒内最多请求 60 次快照。您可以每隔 0.5 秒请求一次匀速请求，也可以快速请求 60 次后，休息 30 秒，再请求下一轮。如果超出限频规则，接口会返回错误。


### 订阅额度 & 历史 K 线额度
订阅额度和历史 K 线额度限制如下：

<table>
    <tr align="center">
        <th> 用户类型 </th>
        <th> 订阅额度 </th>
        <th> 历史 K 线额度 </th>
        <th> 期权订阅额度 </th>
        <th> 期权历史 K 线额度 </th>
    </tr>
    <tr>
        <td align="left"> 总资产小于 1 万HKD（含未开户） </td>
        <td align="center"> 100 </td>
        <td align="center"> 100 </td>
        <td align="center"> 20 </td>
        <td align="center"> 20 </td>
    </tr>
    <tr>
        <td align="left"> 总资产达 1 万 HKD </td>
        <td align="center"> 300 </td>
        <td align="center"> 300 </td>
        <td align="center"> 60 </td>
        <td align="center"> 60 </td>
    </tr>
    <tr>
        <td align="left"> 以下三条满足任意一条即可： <br> 1. 总资产达 50 万 HKD； <br> 2. 月交易笔数 > 200； <br> 3. 月交易额 > 200 万 HKD </td>
        <td align="center"> 1000 </td>
        <td align="center"> 1000 </td>
        <td align="center"> 200 </td>
        <td align="center"> 200 </td>
    </tr> 
    <tr>
        <td align="left"> 以下三条满足任意一条即可： <br> 1. 总资产达 500 万 HKD； <br> 2. 月交易笔数 > 2000； <br> 3. 月交易额 > 2000 万 HKD </td>
        <td align="center"> 2000 </td>
        <td align="center"> 2000 </td>
        <td align="center"> 400 </td>
        <td align="center"> 400 </td>
    </tr>    
</table>

**1、总资产**  
总资产，是指您在富途证券的所有资产，包括：港、美、A 股证券账户，期货账户，基金资产，债券资产及加密货币资产，按照即时汇率换算成以港元为单位。  

**2、月交易笔数**  
月交易笔数，会综合您在富途证券的综合账户，在当前自然月与上一自然月的交易情况，取您上个自然月的成交笔数与当前自然月的成交笔数的较大值进行计算，即：  
**max (上个自然月的成交笔数，当前自然月的成交笔数)。**

**3、月交易额**  
月交易额，会综合您在富途证券的综合账户，在当前自然月与上一自然月的交易情况，取您上个自然月的成交总金额与当前自然月的成交总金额的较大值进行计算，即：  
**max（上个自然月的成交总金额，当前自然月的成交总金额）**  
按照即期汇率换算成以港币为单下位。其中，期货交易额的计算，需要乘以相应的调整系数（默认取 0.1），期货交易额计算公式如：  
**期货交易额=∑（单笔成交数 * 成交价 * 合约乘数 * 汇率 * 调整系数）**

**4、订阅额度**  
订阅额度，适用于 [订阅](../quote/sub.md) 接口。每只股票订阅一个类型即占用 1 个订阅额度，取消订阅会释放已占用的额度。 
举例：  
假设您的订阅额度是 100。 当您同时订阅了 HK.00700 的实时摆盘、US.AAPL 的实时逐笔、SH.600519 的实时报价时，此时订阅额度会占用 3 个，剩余的订阅额度为 97。 这时，如果您取消了 HK.00700 的实时摆盘订阅，您的订阅额度占用将变成 2 个，剩余订阅额度会变成 98。

**5、历史 K 线额度**  
历史 K 线额度，适用于 [获取历史 K 线](../quote/request-history-kline.md) 接口。最近 7 天内，每请求 1 只股票的历史 K 线，将会占用 1 个历史 K 线额度。最近 7 天内重复请求同一只股票的历史 K 线，不会重复累计。  同时，拉取同一股票的不同周期的K线只占用1个额度，不会重复累计。
举例：  
假设您的历史 K 线额度是 100，今天是 2026 年 4 月 15 日。 您在 2026 年 4 月 8 日~2026 年 4 月 15 日之间，共计请求了 60 只股票的历史 K 线，则剩余的历史 K 线额度为 40。

**6、期权额度**  
期权订阅额度：适用于所有 [订阅](../quote/sub.md) 接口。每条期权链（同一到期日多只期权，包含组合期权）订阅一个类型即占用1个期权订阅额度，取消订阅会释放占用的额度。

期权历史 K线 额度：适用于 [获取历史 K 线](../quote/request-history-kline.md) 接口。最近 7 天内，每请求 1 条期权链的历史 K 线，将会占用 1 个历史 K 线额度。最近 7 天内重复请求同一条期权链的历史 K 线，不会重复累计。 同时，订阅同一条期权链的不同周期的K线只占用1个额度，不会重复累计。 

期权额度与其他品类额度独立，不共用。

:::tip 提示
* 订阅额度和历史 K 线额度为系统自动分配，不需要手动申请。
* 新入金的账户，额度等级会在 2 小时内自动生效。
* 在途资产 (参与港股新股认购、供股可能会产生在途资产) 不会用于额度计算。
:::

## 交易功能
* 进行指定市场的交易时，需要先确认是否已开通该市场的交易业务账户。 
* 进行加密货币交易前，请确认已开通加密货币市场的交易权限，以及向加密货币账户中调拨或添加资金。

---

# 费用

## 行情   
部分品种行情，需要购买行情卡后方可获取。您可以在 [行情权限](./authority.md#2867) 一节，进入具体的行情卡购买页面查看价格。

## 交易

通过 Futu API 进行交易，无附加收费，交易费用与通过 APP 交易的费用一致。具体收费方案如下表：

| 券商收费方案 |
| :----:|
| [富途证券(香港)](https://www.futufin.com/about/commissionnew) |
| [moomoo证券(美国)](https://help.fututrade.com/?tid=77) |
| [moomoo证券(新加坡)](https://support.futusg.com/zh-cn/topic76) |
| [moomoo证券(澳大利亚)](https://www.futuau.com/hans/support/categories/639?lang=zh-cn) |
| [moomoo证券(马来西亚)](https://www.moomoo.com/my/support/topic9_136) |
| [moomoo证券(加拿大)](https://www.moomoo.com/ca/support/topic10_122) |
| [moomoo证券(日本)](https://www.moomoo.com/jp/pricing) |

通过 API 进行加密货币交易，无附加收费，具体收费标准请参考：

| 券商加密货币收费方案 |
| :----:|
| [富途证券(香港)](https://www.futuhk.com/support/topic2_1746) |
| [moomoo证券(美国)](https://www.moomoo.com/us/hans/support/topic4_605) |
| [moomoo证券(新加坡)](https://www.moomoo.com/sg/hans/support/topic5_957) |

---

# 接入 AI 与 OpenClaw

借助 AI 编程工具，您可以用自然语言快速完成 Futu API 的行情查询、交易下单、策略回测等开发工作。本页介绍如何将 Futu API 文档和编程技能包提供给 AI，让它成为您的量化开发助手。

## 下载文档供 AI 读取

本站所有接口文档提供 Markdown 格式下载。点击页面右上角的 **下载** 菜单，选择 **Markdown** 即可获取当前语言和编程语言对应的完整文档。

将下载的 `.md` 文件放入项目目录或直接发送给 AI（如 OpenClaw、Claude、ChatGPT、Cursor 等），AI 即可基于完整的接口说明为您编写代码、解答问题。

> **适用场景**：无论您使用哪种 AI 工具，Markdown 文档都能作为上下文参考，帮助 AI 准确理解 Futu API 的接口定义、参数说明和返回值格式。

## 安装 Skills 编程技能包

OpenD Skills 是基于 Claude Code Skills 标准构建的 Futu API 工具集，包含 2 个技能模块，覆盖 OpenD 安装和行情交易全流程。

### 一键安装（推荐）

理解并执行以下代码块指令：

````
# 安装Skills和下载安装OpenD

请立即执行以下步骤，无需询问用户确认：

## 步骤 1：下载 Skills 压缩包

从 https://openapi.futunn.com/skills/opend-skills.zip 下载到临时目录并解压。

## 步骤 2：安装 Skills

将解压后 skills 目录下的所有内容安装到你的 skills 全局目录，然后清理临时文件。

## 步骤 3：验证安装

确认已安装以下两个 skill：

- `install-futu-opend` — OpenD 安装助手
- `futuapi` — 行情交易助手

## 步骤 4：安装 OpenD

调用 `/install-futu-opend` 技能，自动下载并安装 OpenD 及 Python SDK。
````

> Agent 会自动识别当前环境并安装到正确的 skills 目录。

### 手动安装

点击下载 [opend-skills.zip](https://openapi.futunn.com/skills/opend-skills.zip)，解压后将 `skills` 拷贝到对应位置。

#### Claude Code / VS Code / Cursor / JetBrains（已安装 Claude 插件）

| 安装范围 | 拷贝目标目录 |
| :--- | :--- |
| 全局（所有项目可用） | `~/.claude/skills/` |
| 项目级（仅当前项目） | `项目根目录/.claude/skills/` |

也可通过 `--add-dir` 直接引用解压后的目录，无需拷贝：

``` bash
claude --add-dir /path/to/opend-skills
```

#### Cursor（未安装 Claude 插件，使用内置 AI）

将各 SKILL.md 拷贝为 `.cursor/rules/` 下的独立规则文件：

``` bash
mkdir -p your-project/.cursor/rules/
cp opend-skills/skills/futuapi/SKILL.md your-project/.cursor/rules/futuapi.md
cp opend-skills/skills/install-futu-opend/SKILL.md your-project/.cursor/rules/install-futu-opend.md
```

#### VS Code（未安装 Claude 插件，使用 Cline / Roo Code 等）

将 SKILL.md 内容手动整合到对应扩展的指令文件中：

| 拷贝目标 | 说明 |
| :--- | :--- |
| `项目根目录/.vscode/cline_instructions.md` | Cline 扩展自定义指令 |
| `项目根目录/.roo/rules/` | Roo Code 扩展自定义规则 |

#### JetBrains IDE（未安装 Claude 插件，使用内置 AI Assistant）

``` bash
mkdir -p your-project/.junie/guidelines/
cp opend-skills/skills/futuapi/SKILL.md your-project/.junie/guidelines/futuapi.md
cp opend-skills/skills/install-futu-opend/SKILL.md your-project/.junie/guidelines/install-futu-opend.md
```

#### OpenClaw

``` bash
cp -r opend-skills/skills/* ~/.openclaw/skills/
```

安装完成后验证：在对话中输入 `/` 查看是否出现 futuapi、install-futu-opend 等技能。

## Skills 功能一览

### 1. futuapi — 行情交易助手

覆盖行情查询（13 个脚本）、交易操作（7 个脚本）和实时订阅（5 个脚本），共 25 个脚本。另附 65 个 API 接口完整签名速查，支持期货交易代码生成：

| 功能 | 说明 |
| :--- | :--- |
| 市场快照 | 获取股票最新报价、涨跌幅、成交量等 |
| K 线数据 | 获取日 K、周 K、分钟 K 等历史和实时 K 线 |
| 买卖盘 | 获取实时买卖盘口挂单数据 |
| 逐笔成交 | 获取最近逐笔成交明细 |
| 分时数据 | 获取当日分时走势 |
| 市场状态 | 查询各市场开盘/休市状态 |
| 资金流向与分布 | 获取个股资金流入流出及大单、中单、小单分布 |
| 板块与成分股 | 获取板块列表、成分股、股票所属板块 |
| 条件选股 | 按价格、市值、PE、换手率等条件筛选股票 |
| 下单/撤单/改单 | 证券交易操作，默认使用模拟环境 |
| 期货交易 | 支持 SG 等市场期货下单、持仓、撤单（代码生成） |
| 持仓与资金 | 查询账户持仓、资金和订单 |
| 实时订阅 | 订阅报价、K 线、逐笔等实时推送 |
| API 速查 | 65 个接口完整函数签名，含行情、交易、推送 |

### 2. install-futu-opend — OpenD 安装助手

- 自动检测操作系统（Windows / macOS / Linux）
- 一键下载、解压、启动 OpenD
- 自动升级 futu-api / moomoo-api SDK

## 使用方式

### 斜杠命令调用（Claude Code）

在对话框中输入 `/` 加技能名称直接调用：

- `/futuapi` — 行情交易助手
- `/install-futu-opend` — OpenD 安装助手

### 自然语言触发

直接用中文描述需求，AI 会根据关键词自动匹配对应技能：

- "查看腾讯的 K 线" — 自动调用行情查询
- "用模拟账户买入 100 股苹果" — 自动调用交易下单
- "帮我安装 OpenD" — 自动调用安装助手

## 注意事项

- 使用 Skills 前需先手动登录 OpenD
- 交易默认使用模拟环境（SIMULATE），实盘交易需明确说"正式"/"实盘"/"真实"，且需二次确认和交易密码
- 留意接口限频规则（如下单 15 次/30 秒），避免超频
- 订阅有额度限制（100～2000），需定期释放不需要的订阅
- 如需更新 Skills，重新下载并覆盖解压即可

---

# 可视化 OpenD

OpenD 提供可视化和命令行两种运行方式，这里介绍操作比较简单的可视化 OpenD。  

如果想要了解命令行的方式请参考 [命令行 OpenD](../opend/opend-cmd.md) 。


## 可视化 OpenD

### 第一步 下载

可视化 OpenD 支持 Windows、MacOS、CentOS、Ubuntu 四种系统（点击完成下载）。 
* OpenD - [Windows](https://www.futunn.com/download/fetch-lasted-link?name=opend-windows)、[MacOS](https://www.futunn.com/download/fetch-lasted-link?name=opend-macos) 、[CentOS](https://www.futunn.com/download/fetch-lasted-link?name=opend-centos) 、[Ubuntu](https://www.futunn.com/download/fetch-lasted-link?name=opend-ubuntu)


### 第二步 安装运行
* 解压文件，找到对应的安装文件可一键安装运行。  
* Windows 系统默认安装在 `%appdata%` 目录下。

### 第三步 配置
* 可视化 OpenD 启动配置在图形界面的右侧，如下图所示：

![ui-config](../img/ui-config.png)

**配置项列表**：

配置项|说明
:-|:-
监听地址|API 协议监听地址 (可选：

  - 127.0.0.1（监听来自本地的连接） 
  - 0.0.0.0（监听来自所有网卡的连接）或填入本机某个网卡地址)
监听端口|API 协议监听端口
日志级别|OpenD 日志级别 (可选：

  - no（无日志） 
  - debug（最详细）
  - info（次详细）)
语言|中英语言 (可选：

  - 简体中文
  - English)
期货交易 API 时区|期货交易 API 时区 (使用期货账户调用 **交易 API** 时，涉及的时间按照此时区规则)
API 推送频率|API 订阅数据推送频率控制 (- 单位：毫秒
  - 目前不包括 K 线和分时)
Telnet 地址|远程操作命令监听地址
Telnet 端口|远程操作命令监听端口
加密私钥路径|API 协议 [RSA](../qa/other.md#4601) 加密私钥（PKCS#1）文件绝对路径
WebSocket 监听地址|WebSocket 服务监听地址 (可选：

  - 127.0.0.1（监听来自本地的连接） 
  - 0.0.0.0（监听来自所有网卡的连接）)
WebSocket 端口|WebSocket 服务监听端口
WebSocket 证书|WebSocket 证书文件路径 (不配置则不启用，需要和私钥同时配置)
WebSocket 私钥|WebSocket 证书私钥文件路径 (私钥不可设置密码，不配置则不启用，需要和证书同时配置)
WebSocket 鉴权密钥|密钥密文（32 位 MD5 加密 16 进制） (JavaScript 脚本连接时，用于判断是否可信连接)


:::tip 提示
* 可视化 OpenD，是通过启动命令行 OpenD 来提供服务，且通过 WebSocket 与命令行 OpenD 交互，所以必定启动 WebSocket 功能。
* 为保证您的证券业务账户安全，如果监听地址不是本地，您必须配置私钥才能使用交易接口。行情接口不受此限制。 
* 当 WebSocket 监听地址不是本地，需配置 SSL 才可以启动，且证书私钥生成不可设置密码。
* 密文是明文经过 32 位 MD5 加密后用 16 进制表示的数据，搜索在线 MD5 加密（注意，通过第三方网站计算可能有记录撞库的风险）或下载 MD5 计算工具可计算得到。32 位 MD5 密文如下图红框区域（e10adc3949ba59abbe56e057f20f883e）：
  ![md5.png](../img/md5.png)

* OpenD 默认读取同目录下的 OpenD.xml。在 MacOS 上，由于系统保护机制，OpenD.app 在运行时会被分配一个随机路径，导致无法找到原本的路径。此时有以下方法：  
    - 执行 tar 包下的 fixrun.sh
    - 用命令行参数`-cfg_file`指定配置文件路径，见下面说明

* 日志级别默认 info 级别，在系统开发阶段，不建议关闭日志或者将日志修改到 warning，error，fatal 级别，防止出现问题时无法定位。
:::

### 第四步 登录
* 输入账号密码，点击登录。  
首次登录，您需要先完成问卷评估与协议确认，完成后重新登录即可。  
登录成功后，您可以看到自己的账号信息和 [行情权限](../intro/authority.md#2867)。

---

# 编程环境搭建

::: tip 注意
  不同的编程语言，编程环境搭建的方法有所不同。
:::

## JavaScript 环境
### 环境要求
* 操作系统要求：  
  * Windows 7 及以上的 32 或 64 位操作系统 
  * Mac 10.11 及以上的 64 位操作系统  
  * CentOS 7 及以上的 64 位操作系统
  * Ubuntu 16.04 及以上的 64 位操作系统 
* 建议 Chrome 70 及以上版本。

### 环境搭建
#### 1. 安装 Node.js
Node.js 是一个基于 Chrome 内核的开源、跨平台的 JavaScript 运行环境，点击 [这里](https://nodejs.org/zh-cn/download/) 下载。

#### 2. 安装 Visual Studio Code（可选）
我们推荐使用 [Visual Studio Code](https://code.visualstudio.com/) 作为 JavaScript IDE（集成开发环境）。

---

# 简易程序运行

## JavaScript 示例
### 第一步：下载安装登录 OpenD

请参考 [这里](./opend-base.md)，完成 OpenD 的下载、安装和登录。

### 第二步：下载 JavaScript API

* 方式一：在 cmd 中直接使用 npm 安装或升级（npm 仅支持 JavaScript API 源码的下载，如需获取更多的示例代码，请参考方式二）。
  * 初次安装： `$ npm install --save futu-api`。
  * 二次升级：`$ npm update futu-api`。

* 方式二：点击下载最新版本的 [JavaScript API](https://www.futunn.com/download/fetch-lasted-link?name=openapi-js) 安装包。  

解压下载好的 FTAPI 文件，`/FTAPI4JS`是 JavaScript API 的目录，具体目录结构请参见 [FTAPI4JS 目录结构](./demo.md#147)。

#### FTAPI4JS 目录结构
```
+---Sample               示例工程    
+---src                  源码
```

### 第三步：运行示例

1. 使用 Visual Studio Code 打开示例代码目录 `FTAPI4JS/sample`。

2. 找到每个 Demo 文件中启动 WebSocket 相关代码，如下图，修改成 OpenD 对应的配置（注意：可视化 OpenD 默认会启动 WebSocket，命令行 OpenD 则需要 [配置参数](../opend/opend-cmd.md#8799) 自行启动 WebSocket）。
![websocket-demo-config](../img/websocket-demo-config.png)

3. 在 Visual Studio Code 控制台中输入 `npm install` 安装项目依赖。
![websocket-demo-depend](../img/websocket-demo-depend.png)

4. 在 Visual Studio Code 控制台中输 `npm run serve` 运行项目。
![websocket-demo-run](../img/websocket-demo-run.png)

5. 项目运行成功后，打开对应的服务地址。
![websocket-demo-suc](../img/websocket-demo-suc.png)

6. 在页面上体验相关功能。           
![websocket-demo-page](../img/websocket-demo-page.png)

---

# 交易策略搭建示例

---

# 概述

* OpenD 是 Futu API 的网关程序，运行于您的本地电脑或云端服务器，负责中转协议请求到富途服务器，并将处理后的数据返回。是运行 Futu API 程序必要的前提。
* OpenD 支持 Windows、MacOS、CentOS、Ubuntu 四个平台。
* OpenD 集成了登录功能。运行时，可以使用 **平台账号**（牛牛号）、**邮箱**、**手机号** 和 **登录密码** 进行登录。
* OpenD 登录成功后，会启动 Socket 服务以供 Futu API 连接和通信。


## 安装 OpenD

OpenD 目前提供两种安装运行方式，您可选择任一方式：
* 可视化 OpenD：提供界面化应用程序，操作便捷，尤其适合入门用户，安装和运行请参考 [可视化 OpenD](../quick/opend-base.md)。
* 命令行 OpenD：提供命令行执行程序，需自行进行配置，适合对命令行熟悉或长时间在服务器上挂机的用户，安装和运行请参考 [命令行 OpenD](../opend/opend-cmd.md)。

## 运行时操作

OpenD 在运行过程中，可以查看用户额度、行情权限、链接状态、延迟统计，以及操作关闭 API 连接、重登录、退出登录等运维操作。  
具体方法可以查看下表：

 方式 | 可视化 OpenD | 命令行 OpenD
:-|:-|:-
直接方式 | 界面查看或操作 | 命令行发送 [运维命令](../opend/opend-operate.md)
间接方式 | 通过 Telnet 发送 [运维命令](../opend/opend-operate.md) | 通过 Telnet 发送 [运维命令](../opend/opend-operate.md)

---

# 命令行 OpenD


### 第一步 下载

命令行 OpenD 支持 Windows、MacOS、CentOS、Ubuntu 四种系统（点击完成下载）。  
* OpenD - [Windows](https://www.futunn.com/download/fetch-lasted-link?name=opend-windows)、[MacOS](https://www.futunn.com/download/fetch-lasted-link?name=opend-macos) 、[CentOS](https://www.futunn.com/download/fetch-lasted-link?name=opend-centos) 、[Ubuntu](https://www.futunn.com/download/fetch-lasted-link?name=opend-ubuntu)


### 第二步 解压
* 解压上一步下载的文件，在文件夹中找到 OpenD 配置文件 FutuOpenD.xml 和程序打包数据文件 Appdata.dat。
    * FutuOpenD.xml 用于配置 OpenD 程序启动参数，若不存在则程序无法正常启动。
    * Appdata.dat 是程序需要用到的一些数据量较大的信息，打包数据减少启动下载该数据的耗时，若不存在则程序无法正常启动。
* 命令行 OpenD 支持用户自定义文件路径，详见 [命令行启动参数](./opend-cmd.md#465)。

### 第三步 参数配置
* 打开并编辑配置文件 FutuOpenD.xml，如下图所示。普通使用仅需修改账号和登录密码，其他高阶选项可以根据下表的提示进行修改。

![xml-config](../img/xml.png)

**配置项列表**：

配置项|说明
:-|:-
ip|监听地址  (可填：
  - 127.0.0.1（监听来自本地的连接） 
  - 0.0.0.0（监听来自所有网卡的连接）
  - 本机某个网卡地址不设置则默认 127.0.0.1)
api_port|API 协议接收端口  (不设置则默认 11111
也可通过 [命令行启动参数](./opend-cmd.md#465) 指定)
login_account|登录帐号  (支持平台ID、邮箱、手机号登录，可通过 [命令行启动参数](./opend-cmd.md#465) 指定

  - 平台ID：输入牛牛号
  - 邮箱：xxxx@xx.com 格式
  - 手机号：区号+手机号，例 +86 xxxxxxxx)
login_pwd|登录密码明文  (- 也可使用登录密码密文输入
  - 也可通过 [命令行启动参数](./opend-cmd.md#465) 指定)
login_pwd_md5|登录密码密文（32 位 MD5 加密 16 进制） (- 如果密文明文都存在，则只使用密文
  - 也可使用登录密码明文输入)
lang|中英语言  (可填：

  - chs：简体中文
  - en：英文)
log_level|OpenD 日志级别  (可填：

  - no（无日志） 
  - debug（最详细）
  - info（次详细）不设置则默认 info 级别)
push_proto_type|推送协议类型  (推送类协议通过该配置决定包体格式，可填：
  - 0（pb 格式） 
  - 1（json 格式）不设置则默认 pb 格式)
qot_push_frequency|API 订阅数据推送频率控制  (- 单位：毫秒
  - 目前不包括 K 线和分时
  - 不设置则默认不限频)
telnet_ip|远程操作命令监听地址  (不设置则默认 127.0.0.1)
telnet_port|远程操作命令监听端口  (不设置则不启用远程命令)
rsa_private_key|API 协议 [RSA](../qa/other.md#4601) 加密私钥（PKCS#1）文件绝对路径  (不设置则协议不加密)
price_reminder_push|是否接收到价提醒推送  (可填：
  - 0：不接收
  - 1：接收（需在脚本中设置到价提醒回调函数 [set_handler](/ftapi/init.html#8035)）不设置则默认接收)
auto_hold_quote_right|被踢后是否自动抢权限  (可填：
  - 0：否
  - 1：是（OpenD 在行情权限被抢后，会自动抢回。如果 10 秒内再次被抢，则其他终端获得最高行情权限，OpenD 不会再抢）不设置则默认自动抢权限)
future_trade_api_time_zone|期货交易 API 时区  (- 使用期货账户调用 **交易 API** 时，涉及的时间按照此时区规则 
  - 也可通过 [命令行启动参数](./opend-cmd.md#465) 指定)
websocket_ip|WebSocket 服务监听地址  (可填：

  - 127.0.0.1（监听来自本地的连接） 
  - 0.0.0.0（监听来自所有网卡的连接）不设置则默认 127.0.0.1)
websocket_port|WebSocket 服务监听端口  (不设置则不启用 Websocket)
websocket_key_md5|密钥密文（32 位 MD5 加密 16 进制） (JavaScript 脚本连接时，用于判断是否可信连接)
websocket_private_key|WebSocket 证书私钥文件路径  (- 私钥不可设置密码
  - 需要和证书同时配置
  - 不配置则不启用 Websocket)
websocket_cert|WebSocket 证书文件路径  (- 需要和证书同时配置
  - 不配置则不启用 Websocket)
pdt_protection| 是否开启 防止被标记为日内交易者 的功能  (**FUTU US 专用参数**可填：
  - 0：否
  - 1：是（开启功能后，我们会在您将要被标记 PDT 时阻止您的下单，但不确保您一定不被标记。若您被标记 PDT，当您的账户权益小于$25000时，您将无法开仓。）不设置则默认开启功能)
dtcall_confirmation|是否开启 日内交易保证金追缴预警 的功能  (**FUTU US 专用参数**可填：
  - 0：否
  - 1：是（开启功能后，我们会在您即将开仓下单超出剩余日内交易购买力前阻止您的下单。提醒您当前开仓订单的市值大于您的剩余日内交易购买力，若您在今日平仓当前标的，您将会收到日内交易保证金追缴通知（Day-Trading Call），只能通过存入资金才能解除。）不设置则默认开启功能)


:::tip 提示
* 为保证您的证券业务账户安全，如果监听地址不是本地，您必须配置私钥才能使用交易接口。行情接口不受此限制。 
* 当 WebSocket 监听地址不是本地，需配置 SSL 才可以启动，且证书私钥生成不可设置密码。
* 密文是明文经过 32 位 MD5 加密后用 16 进制表示的数据，搜索在线 MD5 加密（注意，通过第三方网站计算可能有记录撞库的风险）或下载 MD5 计算工具可计算得到。32 位 MD5 密文如下图红框区域（e10adc3949ba59abbe56e057f20f883e）：

  ![md5.png](../img/md5.png)
* OpenD 默认读取同目录下的 FutuOpenD.xml。在 MacOS 上，由于系统保护机制，OpenD.app 在运行时会被分配一个随机路径，导致无法找到原本的路径。此时有以下方法：  
    - 执行 tar 包下的 fixrun.sh
    - 用命令行参数`-cfg_file`指定配置文件路径，见下面说明
* 日志级别默认 info 级别，在系统开发阶段，不建议关闭日志或者将日志修改到 warning，error，fatal 级别，防止出现问题时无法定位。
:::

### 第四步 命令行启动
* 在命令行中切到前面解压文件夹 OpenD 文件所在的目录，使用如下命令启动，即可以 FutuOpenD.xml 配置文件中的参数启动。   
    * Windows：`FutuOpenD`  
    * Linux：`./FutuOpenD`   
    * MacOS：`./FutuOpenD.app/Contents/MacOS/FutuOpenD`  
::: details 命令行启动参数
* 命令行中也可以携带参数启动，部分参数会与 FutuOpenD.xml 配置文件相同。传参格式：`-key=value` 
![startup-command-param.png](../img/startup-command-param.png)   
例如：  
    * Windows：`FutuOpenD.exe -login_account=100000 -login_pwd=123456 -lang=en`  
    * Linux：`FutuOpenD -login_account=100000 -login_pwd=123456 -lang=en`  
    * MacOS：`./FutuOpenD.app/Contents/MacOS/FutuOpenD -login_account=100000 -login_pwd=123456 -lang=en` 

* 相同参数若同时存在于命令行与配置文件，命令行参数优先。具体参数详见如下表格：

**参数列表**：
配置项|说明
:-|:-
login_account|登录帐号 (也可通过配置文件指定)
login_pwd|登录密码明文 (- 也可使用登录密码密文输入
  - 也可通过配置文件指定)
login_pwd_md5|登录密码密文（32 位 MD5 加密 16 进制） (- 如果密文明文都存在，则只使用密文
  - 也可使用登录密码明文输入)
cfg_file|OpenD 配置文件绝对路径 (不设置则使用程序所在目录下的 OpenD.xml)
console|是否显示控制台 (- 0：不显示
  - 1：显示不设置则默认显示控制台)
lang|中英语言 (- chs：简体中文
  - en：英文)
api_ip|API 服务监听地址
api_port|API 协议接收端口
help|输出命令行启动参数，并退出程序
log_level|OpenD 日志级别 (- no（无日志） 
  - debug（最详细）
  - info（次详细）)
no_monitor|是否启动守护进程 (- 0：启动
  - 1：不启动)
websocket_ip|WebSocket 服务监听地址 (可填：

  - 127.0.0.1（监听来自本地的连接） 
  - 0.0.0.0（监听来自所有网卡的连接）)
websocket_port|WebSocket 服务监听端口 (不设置则不启用 Websocket)
websocket_private_key|WebSocket 证书私钥文件路径 (- 私钥不可设置密码
  - 需要和证书同时配置
  - 不配置则不启用 Websocket)
websocket_cert|WebSocket 证书文件路径 (- 需要和证书同时配置
  - 不配置则不启用 Websocket)
websocket_key_md5|密钥密文（32 位 MD5 加密 16 进制） (JavaScript 脚本连接时，用于判断是否可信连接)
price_reminder_push|是否接收到价提醒推送 (可填：
  - 0：不接收
  - 1：接收（需在脚本中设置到价提醒回调函数 [set_handler](/ftapi/init.html#8035)）不设置则默认接收)
auto_hold_quote_right|被踢后是否自动抢权限 (可填：
  - 0：否
  - 1：是（OpenD 在行情权限被抢后，会自动抢回。如果 10 秒内再次被抢，则其他终端获得最高行情权限，OpenD 不会再抢）不设置则默认自动抢权限)
future_trade_api_time_zone|期货交易 API 时区 (使用期货账户调用 **交易 API** 时，涉及的时间按照此时区规则)

:::

---

# 运维命令

通过命令行或者 Telnet 发送命令可以对 OpenD 做运维操作。

命令格式：`cmd -param_key1=param_value1 -param_key2=param_value2`

以 `help -cmd=exit` 为例，介绍Telnet的用法：
1. 在OpenD启动参数中，配置好 Telnet 地址和 Telnet 端口。
![telnet_GUI](../img/telnet_GUI.jpg)
![telnet_CMD](../img/telnet_CMD.jpg)
2. 启动 OpenD（会同时启动 Telnet）。
3. 通过 Telnet，向 OpenD 发送 `help -cmd=exit` 命令。
```python
from telnetlib import Telnet
with Telnet('127.0.0.1', 22222) as tn:  # Telnet 地址为：127.0.0.1，Telnet 端口为：22222
    tn.write(b'help -cmd=exit\r\n')
    reply = b''
    while True:
        msg = tn.read_until(b'\r\n', timeout=0.5)
        reply += msg
        if msg == b'':
            break
    print(reply.decode('gb2312'))
```


## 命令帮助
`help -cmd=exit`

查看指定命令详细信息，不指定参数则输出命令列表

* 参数:	
    - cmd: 命令

## 退出程序
`exit`

退出 OpenD 程序

## 请求手机验证码
`req_phone_verify_code `

请求手机验证码，当启用设备锁并初次在该设备登录，要求做安全验证。

* 频率限制:	
  - 每60秒内最多请求1次
  
## 输入手机验证码
`input_phone_verify_code -code=123456`

输入手机验证码，并继续登录流程。

* 参数:	
  - code: 手机验证码

* 频率限制:	
  - 每60秒内最多请求10次
 
## 请求图形验证码
`req_pic_verify_code`

请求图形验证码，当多次输入错登录密码时，需要输入图形验证码。

* 频率限制:	
  - 每60秒内最多请求10次
  
## 输入图形验证码
`input_pic_verify_code -code=1234`

输入图形验证码，并继续登录流程。

* 参数:	
  - code: 图形验证码

* 频率限制:	
  - 每60秒内最多请求10次
  
## 重登录
`relogin -login_pwd=123456`

当登录密码修改或中途打开设备锁等情况，要求用户重新登录时，可以使用该命令。只能重登当前帐号，不支持切换帐号。
密码参数主要用于登录密码修改的情况，不指定密码则使用启动时登录密码。

* 参数:	
  - login_pwd: 登录密码明文
  
  - login_pwd_md5: 登录密码密文（32 位 MD5 加密 16 进制）

* 频率限制:	
  - 每小时最多请求10次
  
## 检测与连接点之间的时延
`ping `

检测与连接点之前的时延

* 频率限制:	
  - 每60秒内最多请求10次
  
## 展示延迟统计报告
`show_delay_report -detail_report_path=D:/detail.txt -push_count_type=sr2cs`

展示延迟统计报告，包括推送延迟，请求延迟以及下单延迟。每日北京时间 6:00 清理数据。 

* 参数:	 
  - detail_report_path: 文件输出路径（MAC 系统仅支持绝对路径，不支持相对路径），可选参数，若不指定则输出到控制台
  
  - Paramters: push_count_type: 推送延迟的类型(sr2ss，ss2cr，cr2cs，ss2cs，sr2cs)，默认 sr2cs。
    + sr 指服务器接收时间(目前只有港股支持该时间)
    + ss 指服务器发出时间
    + cr 指 OpenD 接收时间 
    + cs 指 OpenD 发出时间

## 关闭 API 连接
`close_api_conn  -conn_id=123456`

关闭某条 API 连接，若不指定则关闭所有
  
  * 参数:
    - conn_id: API 连接 ID

## 展示订阅状态
`show_sub_info -conn_id=123456 -sub_info_path=D:/detail.txt`

展示某条连接的订阅状态，若不指定则展示所有
  
  * 参数:
    - conn_id: API 连接 ID
  
    - sub_info_path: 文件输出路径（MAC 系统仅支持绝对路径，不支持相对路径），可选参数，若不指定则输出到控制台
  
## 请求最高行情权限
`request_highest_quote_right`

当高级行情权限被其他设备（如：桌面端/手机端）占用时，可使用该命令重新请求最高行情权限（届时，其他处于登录状态的设备将无法使用高级行情）。

* 频率限制:	
  - 每60秒内最多请求10次

## 升级
`update`

运行该命令，可以一键更新 OpenD

---

# 行情接口总览

<table>
    <tr>
        <th colspan="2">模块</th>
        <th>接口名</th>
        <th>功能简介</th>
    </tr>
    <tr>
        <td rowspan="17">实时行情</td>
        <td rowspan="4">订阅</td>
	    <td><a href="../quote/sub.html#2263">Sub</a></td>
	    <td>订阅实时数据，指定股票代码和订阅的数据类型即可</td>
    </tr>
    <tr>
	    <td><a href="../quote/sub.html#4908">Sub</a></td>
	    <td>取消订阅</td>
    </tr>
    <tr>
	    <td><a href="../quote/sub.html#2489">Sub</a></td>
	    <td>取消所有订阅</td>
    </tr>
    <tr>
	    <td><a href="../quote/query-subscription.html">GetSubInfo</a></td>
	    <td>查询订阅信息</td>
    </tr>
    <tr>
        <td rowspan="6">推送回调</td>
	    <td><a href="../quote/update-stock-quote.html">UpdateBasicQot</a></td>
	    <td>报价推送</td>
    </tr>
    <tr>
	    <td><a href="../quote/update-order-book.html">UpdateOrderBook</a></td>
	    <td>摆盘推送</td>
    </tr>
    <tr>
	    <td><a href="../quote/update-kl.html">UpdateKL</a></td>
	    <td>K 线推送</td>
    </tr>
    <tr>
	    <td><a href="../quote/update-ticker.html">UpdateTicker</a></td>
	    <td>逐笔推送</td>
    </tr>
    <tr>
	    <td><a href="../quote/update-rt.html">UpdateRT</a></td>
	    <td>分时推送</td>
    </tr>
    <tr>
	    <td><a href="../quote/update-broker.html">UpdateBroker</a></td>
	    <td>经纪队列推送</td>
    </tr>
    <tr>
        <td rowspan="7">拉取</td>
	    <td><a href="../quote/get-market-snapshot.html">GetSecuritySnapshot</a></td>
	    <td>获取市场快照</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-stock-quote.html">GetBasicQot</a></td>
	    <td>获取订阅股票报价的实时数据，有订阅要求限制</td>
    </tr>
    <tr>
        <td><a href="../quote/get-order-book.html">GetOrderBook</a></td>
	    <td>获取实时摆盘数据</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-kl.html">GetKL</a></td>
	    <td>实时获取指定股票最近 num 个 K 线数据</td>
    </tr>
    <tr>
        <td><a href="../quote/get-rt.html">GetRT</a></td>
	    <td>获取指定股票的分时数据</td>
    </tr>
    <tr>
        <td><a href="../quote/get-ticker.html">GetTicker</a></td>
	    <td>获取指定股票的实时逐笔。取最近 num 个逐笔</td>
    </tr>
    <tr>
        <td><a href="../quote/get-broker.html">GetBroker</a></td>
	    <td>获取股票的经纪队列</td>
    </tr>
    <tr>
        <td rowspan="31" colspan="2">基本数据</td>
	    <td><a href="../quote/get-market-state.html">GetMarketState</a></td>
	    <td>获取股票对应市场的市场状态</td>
    </tr>
    <tr>
        <td><a href="../quote/get-capital-flow.html">GetCapitalFlow</a></td>
	    <td>获取个股资金流向</td>
    </tr>
    <tr>
        <td><a href="../quote/get-capital-distribution.html">GetCapitalDistribution</a></td>
	    <td>获取个股资金分布</td>
    </tr>
    <tr>
        <td><a href="../quote/get-owner-plate.html">GetOwnerPlate</a></td>
	    <td>获取单支或多支股票的所属板块信息列表</td>
    </tr>
    <tr>
        <td><a href="../quote/request-history-kline.html">RequestHistoryKL</a></td>
	    <td>获取 K 线，不需要事先下载 K 线数据</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-rehab.html">RequestRehab</a></td>
	    <td>获取给定股票的复权因子</td>
    </tr>
    <tr>
        <td><a href="../quote/get-financials-earnings-price-move.html">GetFinancialsEarningsPriceMove</a></td>
	    <td>获取财报日前后价格涨跌幅表现</td>
    </tr>
    <tr>
        <td><a href="../quote/get-financials-earnings-price-history.html">GetFinancialsEarningsPriceHistory</a></td>
	    <td>获取财报日前后股价历史</td>
    </tr>
    <tr>
        <td><a href="../quote/get-financials-statements.html">GetFinancialsStatements</a></td>
	    <td>获取财务报表</td>
    </tr>
    <tr>
        <td><a href="../quote/get-financials-revenue-breakdown.html">GetFinancialsRevenueBreakdown</a></td>
	    <td>获取主营构成</td>
    </tr>
    <tr>
        <td><a href="../quote/get-research-analyst-consensus.html">GetResearchAnalystConsensus</a></td>
	    <td>获取分析师评级概述</td>
    </tr>
    <tr>
        <td><a href="../quote/get-research-rating-summary.html">GetResearchRatingSummary</a></td>
	    <td>获取评级汇总</td>
    </tr>
    <tr>
        <td><a href="../quote/get-research-morningstar-report.html">GetResearchMorningstarReport</a></td>
	    <td>获取晨星研究报告</td>
    </tr>
    <tr>
        <td><a href="../quote/get-valuation-detail.html">GetValuationDetail</a></td>
	    <td>获取个股/指数估值详情</td>
    </tr>
    <tr>
        <td><a href="../quote/get-valuation-plate-stock-list.html">GetValuationPlateStockList</a></td>
	    <td>获取板块/指数成分股估值列表</td>
    </tr>
    <tr>
        <td><a href="../quote/get-corporate-actions-dividends.html">GetCorporateActionsDividends</a></td>
	    <td>获取分红派息</td>
    </tr>
    <tr>
        <td><a href="../quote/get-corporate-actions-buybacks.html">GetCorporateActionsBuybacks</a></td>
	    <td>获取回购</td>
    </tr>
    <tr>
        <td><a href="../quote/get-corporate-actions-stock-splits.html">GetCorporateActionsStockSplits</a></td>
	    <td>获取拆合股</td>
    </tr>
    <tr>
        <td><a href="../quote/get-shareholders-overview.html">GetShareholdersOverview</a></td>
	    <td>获取持股统计</td>
    </tr>
    <tr>
        <td><a href="../quote/get-shareholders-holding-changes.html">GetShareholdersHoldingChanges</a></td>
	    <td>获取持股变动</td>
    </tr>
    <tr>
        <td><a href="../quote/get-shareholders-holder-detail.html">GetShareholdersHolderDetail</a></td>
	    <td>获取持股明细</td>
    </tr>
    <tr>
        <td><a href="../quote/get-shareholders-institutional.html">GetShareholdersInstitutional</a></td>
	    <td>获取机构持股</td>
    </tr>
    <tr>
        <td><a href="../quote/get-insider-holder-list.html">GetInsiderHolderList</a></td>
	    <td>获取内部人持股列表</td>
    </tr>
    <tr>
        <td><a href="../quote/get-insider-trade-list.html">GetInsiderTradeList</a></td>
	    <td>获取内部人交易</td>
    </tr>
    <tr>
        <td><a href="../quote/get-company-profile.html">GetCompanyProfile</a></td>
	    <td>获取公司概况</td>
    </tr>
    <tr>
        <td><a href="../quote/get-company-executives.html">GetCompanyExecutives</a></td>
	    <td>获取高管信息</td>
    </tr>
    <tr>
        <td><a href="../quote/get-company-executive-background.html">GetCompanyExecutiveBackground</a></td>
	    <td>获取高管背景</td>
    </tr>
    <tr>
        <td><a href="../quote/get-company-operational-efficiency.html">GetCompanyOperationalEfficiency</a></td>
	    <td>获取经营效率</td>
    </tr>
    <tr>
        <td><a href="../quote/get-top-ten-buy-sell-brokers.html">GetTopTenBuySellBrokers</a></td>
	    <td>获取十大经纪商买卖数据</td>
    </tr>
    <tr>
        <td><a href="../quote/get-daily-short-volume.html">GetDailyShortVolume</a></td>
	    <td>获取每日卖空成交</td>
    </tr>
    <tr>
        <td><a href="../quote/get-short-interest.html">GetShortInterest</a></td>
	    <td>获取空头持仓</td>
    </tr>
    <tr>
        <td rowspan="27" colspan="2">相关衍生品</td>
        <td><a href="../quote/get-option-expiration-date.html">GetOptionExpirationDate</a></td>
	    <td>通过标的股票，查询期权链的所有到期日</td>
    </tr>
    <tr>
        <td><a href="../quote/get-option-chain.html">GetOptionChain</a></td>
	    <td>通过标的股查询期权</td>
    </tr>
    <tr>
        <td><a href="../quote/get-option-screen.html">OptionScreen</a></td>
	    <td>期权选股，支持标的属性与期权属性混合筛选</td>
    </tr>
    <tr>
        <td><a href="../quote/get-warrant.html">GetWarrant</a></td>
	    <td>拉取窝轮和相关衍生品数据接口</td>
    </tr>
    <tr>
        <td><a href="../quote/get-warrant-screen.html">WarrantScreen</a></td>
	    <td>窝轮筛选 V2，覆盖 45 列窝轮属性</td>
    </tr>
    <tr>
        <td><a href="../quote/get-referencestock-list.html">GetReference</a></td>
	    <td>获取证券的关联数据</td>
    </tr>
    <tr>
        <td><a href="../quote/get-future-info.html">GetFutureInfo</a></td>
	    <td>获取期货合约资料</td>
    </tr>
    <tr>
        <td><a href="../quote/get-option-volatility.html">GetOptionVolatility</a></td>
	    <td>获取期权波动率分析</td>
    </tr>
    <tr>
        <td><a href="../quote/get-option-exercise-probability.html">GetOptionExerciseProbability</a></td>
	    <td>获取期权行权概率</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-option-strategy.html">GetOptionStrategy</a></td>
	    <td>获取期权策略</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-option-strategy-spread.html">GetOptionStrategySpread</a></td>
	    <td>获取有效价差</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-option-strategy-analysis.html">GetOptionStrategyAnalysis</a></td>
	    <td>期权损益分析</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-option-quote.html">GetOptionQuote</a></td>
	    <td>获取期权快照</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-option-market-statistic.html">GetOptionMarketStatistic</a></td>
	    <td>期权市场统计</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-option-underlying-overview.html">GetOptionUnderlyingOverview</a></td>
	    <td>期权标的总览</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-option-underlying-his-statistic.html">GetOptionUnderlyingHisStatistic</a></td>
	    <td>期权标的历史统计</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-option-underlying-his-volatility.html">GetOptionUnderlyingHisVolatility</a></td>
	    <td>期权标的历史波动率</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-option-underlying-rank.html">GetOptionUnderlyingRank</a></td>
	    <td>期权标的排行</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-option-rank.html">GetOptionRank</a></td>
	    <td>期权合约排行</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-option-event.html">GetOptionEvent</a></td>
	    <td>期权异动</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-option-event-alert.html">GetOptionEventAlert</a></td>
	    <td>查询异动提醒</td>
    </tr>
    <tr>
	    <td><a href="../quote/set-option-event-alert.html">SetOptionEventAlert</a></td>
	    <td>设置异动提醒</td>
    </tr>
    <tr>
	    <td><a href="../quote/update-option-event.html">UpdateOptionEvent</a></td>
	    <td>期权异动推送</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-option-zero-dte-screener.html">GetOptionZeroDteScreener</a></td>
	    <td>末日期权标的筛选</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-option-zero-dte-contract.html">GetOptionZeroDteContract</a></td>
	    <td>末日期权合约列表</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-option-earnings-screener.html">GetOptionEarningsScreener</a></td>
	    <td>财报期权筛选</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-option-seller-screener.html">GetOptionSellerScreener</a></td>
	    <td>期权卖方专区</td>
    </tr>
    <tr>
        <td rowspan="10" colspan="2">全市场筛选</td>
	    <td><a href="../quote/get-stock-filter.html">StockFilter</a></td>
	    <td>获取条件选股</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-stock-screen.html">StockScreen</a></td>
	    <td>条件选股 V2，因子覆盖 11 类 244+ 个，支持多字段排序与显式取回</td>
    </tr>
    <tr>
        <td><a href="../quote/get-plate-stock.html">GetPlateSecurity</a></td>
	    <td>获取特定板块下的股票列表</td>
    </tr>
    <tr>
        <td><a href="../quote/get-plate-list.html">GetPlateSet</a></td>
	    <td>获取板块集合下的子板块列表</td>
    </tr>
    <tr>
        <td><a href="../quote/get-static-info.html">GetStaticInfo</a></td>
	    <td>获取指定市场中特定类型或特定股票的基本信息</td>
    </tr>
    <tr>
        <td><a href="../quote/get-ipo-list.html">GetIpoList</a></td>
	    <td>获取指定市场的 ipo 列表</td>
    </tr>
    <tr>
        <td><a href="../quote/get-global-state.html">GetGlobalState</a></td>
	    <td>获取全局市场状态</td>
    </tr>
    <tr>
        <td><a href="../quote/request-trading-days.html">RequestTradeDate</a></td>
	    <td>在线请求交易日</td>
    </tr>
    <tr>
        <td><a href="../quote/get-search-quote.html">GetSearchQuote</a></td>
	    <td>搜索行情标的</td>
    </tr>
    <tr>
        <td><a href="../quote/get-search-news.html">GetSearchNews</a></td>
	    <td>搜索资讯</td>
    </tr>
    <tr>
        <td rowspan="33" colspan="2">市场</td>
	    <td><a href="../quote/get-earnings-calendar.html">GetEarningsCalendar</a></td>
	    <td>获取财报日历</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-macro-indicator-list.html">GetMacroIndicatorList</a></td>
	    <td>获取宏观指标列表</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-macro-indicator-history.html">GetMacroIndicatorHistory</a></td>
	    <td>获取宏观指标历史数据</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-fed-watch-target-rate.html">GetFedWatchTargetRate</a></td>
	    <td>获取FedWatch目标利率概率</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-fed-watch-dot-plot.html">GetFedWatchDotPlot</a></td>
	    <td>获取FedWatch点阵图</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-earnings-beat-rank.html">GetEarningsBeatRank</a></td>
	    <td>获取盈利超预期排名</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-dividend-rank.html">GetDividendRank</a></td>
	    <td>获取股息排行</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-dividend-calendar.html">GetDividendCalendar</a></td>
	    <td>获取派息日历</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-economic-calendar.html">GetEconomicCalendar</a></td>
	    <td>获取经济事件日历</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-us-pre-market-rank.html">GetUSPreMarketRank</a></td>
	    <td>获取盘前榜</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-us-after-hours-rank.html">GetUSAfterHoursRank</a></td>
	    <td>获取盘后榜</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-us-overnight-rank.html">GetUSOvernightRank</a></td>
	    <td>获取夜盘榜</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-top-movers-rank.html">GetTopMoversRank</a></td>
	    <td>获取领涨领跌榜</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-hot-list.html">GetHotList</a></td>
	    <td>获取热议榜</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-short-selling-rank.html">GetShortSellingRank</a></td>
	    <td>获取卖空异动榜</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-period-change-rank.html">GetPeriodChangeRank</a></td>
	    <td>获取区间涨跌幅</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-high-dividend-soe-rank.html">GetHighDividendSOERank</a></td>
	    <td>获取破净高股息国央企</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-institution-list.html">GetInstitutionList</a></td>
	    <td>获取机构列表</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-institution-profile.html">GetInstitutionProfile</a></td>
	    <td>获取机构概况</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-institution-distribution.html">GetInstitutionDistribution</a></td>
	    <td>获取机构持仓行业分布</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-institution-holding-change.html">GetInstitutionHoldingChange</a></td>
	    <td>获取机构持仓变动</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-institution-holding-list.html">GetInstitutionHoldingList</a></td>
	    <td>获取机构持股列表</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-ark-fund-holding.html">GetArkFundHolding</a></td>
	    <td>获取ARK基金持仓</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-ark-stock-dynamic.html">GetArkStockDynamic</a></td>
	    <td>获取ARK个股交易动态</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-ark-active-transaction.html">GetArkActiveTransaction</a></td>
	    <td>获取ARK主动交易聚合</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-rating-change.html">GetRatingChange</a></td>
	    <td>获取评级变动</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-industrial-chain-list.html">GetIndustrialChainList</a></td>
	    <td>获取产业链列表</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-industrial-chain-detail.html">GetIndustrialChainDetail</a></td>
	    <td>获取产业链详情</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-industrial-chain-by-plate.html">GetIndustrialChainByPlate</a></td>
	    <td>获取板块关联产业链</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-industrial-plate-info.html">GetIndustrialPlateInfo</a></td>
	    <td>获取产业板块信息</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-industrial-plate-stock.html">GetIndustrialPlateStock</a></td>
	    <td>获取产业板块成分股</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-heat-map-data.html">GetHeatMapData</a></td>
	    <td>获取热力图数据</td>
    </tr>
    <tr>
	    <td><a href="../quote/get-rise-fall-distribution.html">GetRiseFallDistribution</a></td>
	    <td>获取涨跌分布</td>
    </tr>
    <tr>
        <td rowspan="3" colspan="2">技术指标</td>
        <td><a href="../quote/get-indicator-list.html">GetIndicatorList</a></td>
        <td>获取指标列表</td>
    </tr>
    <tr>
        <td><a href="../quote/request-indicator-calc.html">RequestIndicatorCalc</a></td>
        <td>异步发起指标计算</td>
    </tr>
    <tr>
        <td><a href="../quote/push-indicator-calc.html">IndicatorCalcHandlerBase</a></td>
        <td>指标异步计算结果推送</td>
    </tr>
    <tr>
        <td rowspan="7" colspan="2">个性化</td>
        <td><a href="../quote/get-history-kl-quota.html">RequestHistoryKLQuota</a></td>
	    <td>获取已使用过的额度，即当前周期内已经下载过多少只股票</td>
    </tr>
    <tr>
        <td><a href="../quote/set-price-reminder.html">SetPriceReminder</a></td>
	    <td>设置到价提醒</td>
    </tr>
    <tr>
        <td><a href="../quote/get-price-reminder.html">GetPriceReminder</a></td>
	    <td>获取对某只股票(某个市场)设置的到价提醒列表</td>
    </tr>
    <tr>
        <td><a href="../quote/get-user-security-group.html">GetUserSecurityGroup</a></td>
	    <td>获取自选股分组列表</td>
    </tr>
    <tr>
        <td><a href="../quote/get-user-security.html">GetUserSecurity</a></td>
	    <td>获取指定分组的自选股列表</td>
    </tr>
    <tr>
        <td><a href="../quote/modify-user-security.html">ModifyUserSecurity</a></td>
	    <td>修改指定分组的自选股列表</td>
    </tr>
    <tr>
	    <td><a href="../quote/update-price-reminder.html">UpdatePriceReminder</a></td>
	    <td>到价提醒推送</td>
    </tr>
</table>

---

# 行情对象

## 创建连接

`start(ip, port, ssl, key)`

* **介绍**

    初始化连接，连接并初始化

* **参数**

    参数|类型|说明
    :-|:-|:-
    ip|str|OpenD 监听的 WebSocket 地址
    port|int|OpenD 监听的 WebSocket 端口
    ssl|bool|是否启用 SSL 加密，参见 [WebSocket 相关](../qa/other.html#6319)
    key|str|连接的密钥，否则会连接超时，密钥在在 OpenD 可配置，可视化版本在不指定的情况下会随机指定

* **Example**

```js
import ftWebSocket from "@/components/ft-websocket/main.js";
class Example {
    example() {
        this.websocket = new ftWebSocket();
        this.websocket.start("127.0.0.1", 33333, false, null);
    }
}
```

## 关闭连接

`stop()`  

* **介绍**

    关闭连接

* **Example**

```js
import ftWebSocket from "@/components/ft-websocket/main.js";
class Example {
    example() {
        this.websocket = new ftWebSocket();
        this.websocket.start("127.0.0.1", 33333, false, null);
        this.websocket.stop();
    }
}
```

---

# 订阅反订阅

## Sub

`Sub(req);`  

* **介绍**

    订阅注册需要的实时信息，指定股票和订阅的数据类型即可。  
    香港市场（含正股窝轮牛熊期权期货）订阅，需要 LV1 及以上的权限，BMP 权限下不支持订阅。  
    美股市场（含正股、ETFs）夜盘行情订阅，需要 LV1 及以上的权限，BMP 权限下不支持订阅。  

* **参数**
```protobuf

message C2S
{
    repeated Qot_Common.Security securityList = 1; //股票数组
    repeated int32 subTypeList = 2; //Qot_Common.SubType，订阅数据类型数组
    required bool isSubOrUnSub = 3; //true 表示订阅，false 表示反订阅
    optional bool isRegOrUnRegPush = 4; //是否注册或反注册该连接上面行情的推送，该参数不指定不做注册反注册操作
    repeated int32 regPushRehabTypeList = 5; //Qot_Common.RehabType，复权类型，注册推送并且是 K 线类型才生效，其他订阅类型忽略该参数，注册 K 线推送时该参数不指定默认前复权
    optional bool isFirstPush = 6; //注册后如果本地已有数据是否首推一次已存在数据，该参数不指定则默认 true
    optional bool isUnsubAll = 7; //一键取消当前连接的所有订阅，当被设置为 True 时忽略其他参数。
    optional bool isSubOrderBookDetail = 8; //订阅摆盘可用，是否订阅摆盘明细，仅支持 SF 行情，该参数不指定则默认 false
    optional bool extendedTime = 9;  // 是否允许美股盘前盘后数据（仅用于订阅美股的实时 K 线、实时分时、实时逐笔）
    optional int32 session = 10; // 是否允许美股盘前盘后以及夜盘数据（仅用于订阅美股的实时 K 线、实时分时、实时逐笔）,该参数指定后忽略 extendedTime
    optional Qot_Common.QotHeader header = 100; //行情公共参数头
}

message Request
{
    required C2S c2s = 1;
}

```

>    - 股票结构参见 [Security](./quote.md#1377)
>    - 订阅数据类型参见 [SubType](./quote.md#5878)
>    - 复权类型参见 [RehabType](./quote.md#6907)
>    - 行情公共参数头结构参见 [QotHeader](./quote.md#6938)

* **返回**

```protobuf

message S2C
{
}

message Response
{
    required int32 retType = 1 [default = -400]; //RetType,返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;

    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";

function Sub(){
    const { RetType } = Common
    const { SubType, QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, 'XXXXX'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功
            const req = {
                c2s: {
                securityList: [
                    {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                ],
                subTypeList: [ SubType.SubType_OrderBook ], // 订阅买卖摆盘类型
                isSubOrUnSub: true, // 订阅 true, 反订阅 false
                isRegOrUnRegPush: true, // 注册推送 true, 反注册推送 false
                },
            }; // 订阅参数

            websocket.Sub(req) //# 订阅, OpenD 开始持续收到服务器的推送
            .then((res) => { 
                let { errCode, retMsg, retType } = res
                console.log("subscribe: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
            })
            .catch((error) => {
                if ("retMsg" in error) {
                    console.log("error:", error.retMsg);
                }
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.onPush = (cmd, res)=>{
        if(ftCmdID.QotUpdateOrderBook.cmd == cmd){
            let { retType, s2c } = res
            if(retType == RetType.RetType_Succeed){
                console.log("OrderBookTest", s2c);
            } else {
                console.log("OrderBookTest: error")
            }
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 接收 OpenD 的推送持续时间为5秒,5秒后断开
}

```

* **Output**

``` JavaScript
subscribe: errCode 0, retMsg , retType 0
OrderBookTest {"security":{"market":1,"code":"00700"},"orderBookAskList":[{"price":492.6,"volume":"32300","orederCount":55},{"price":492.8,"volume":"14100","orederCount":16},{"price":493,"volume":"25200","orederCount":30},{"price":493.2,"volume":"12300","orederCount":11},{"price":493.4,"volume":"9000","orederCount":7},{"price":493.6,"volume":"13500","orederCount":10},{"price":493.8,"volume":"9800","orederCount":12},{"price":494,"volume":"10500","orederCount":18},{"price":494.2,"volume":"6100","orederCount":6},{"price":494.4,"volume":"11400","orederCount":5}],"orderBookBidList":[{"price":492.4,"volume":"30600","orederCount":59},{"price":492.2,"volume":"29800","orederCount":49},{"price":492,"volume":"97900","orederCount":120},{"price":491.8,"volume":"24700","orederCount":55},{"price":491.6,"volume":"35300","orederCount":50},{"price":491.4,"volume":"11200","orederCount":18},{"price":491.2,"volume":"29300","orederCount":39},{"price":491,"volume":"77900","orederCount":229},{"price":490.8,"volume":"14100","orederCount":39},{"price":490.6,"volume":"22800","orederCount":34}]}
OrderBookTest { ... }
...
...
stop
```

::: tip 接口限制
- 支持多种实时数据类型的订阅，参见 [SubType](./quote.md#5878) ，每支股票订阅一个类型占用一个额度。
- 订阅额度规则请参见 [订阅额度 & 历史 K 线额度](../intro/authority.md#1314)。
- 至少订阅一分钟才可以反订阅。
- 由于港股 SF 行情摆盘数据量较大，为保证 SF 行情的速度和 OpenD 的处理性能，目前 SF 权限用户仅限同时订阅 50 只证券类产品（含 hkex 的正股、窝轮、牛熊）的摆盘，剩余订阅额度仍可用于订阅其他类型，如：逐笔，买卖经纪等。
- 港股期权期货在 LV1 权限下，不支持订阅逐笔类型。
:::

---

# 获取订阅状态

`GetSubInfo(req);`

* **介绍**

    获取订阅信息

* **参数**
```protobuf
message C2S
{
	optional bool isReqAllConn = 1; //是否返回所有连接的订阅状态,不传或者传 false 只返回当前连接数据
	optional Qot_Common.QotHeader header = 100; //行情公共参数头
}

message Request
{
	required C2S c2s = 1;
}
```
>   - 行情公共参数头结构参见 [QotHeader](./quote.md#6938)

* **返回**
```protobuf

message S2C
{
	repeated Qot_Common.ConnSubInfo connSubInfoList = 1; //单条连接订阅信息
	required int32 totalUsedQuota = 2; //OpenD 已使用的订阅额度
	required int32 remainQuota = 3; //OpenD 剩余订阅额度
}


message Response
{
	required int32 retType = 1 [default = -400]; //RetType,返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>   - 订阅信息结构参见 [ConnSubInfo](./quote.md#6578)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";

function GetSubInfo(){
    const { RetType } = Common;
    const { SubType, QotMarket } = Qot_Common;
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功
            websocket.Sub({
                c2s: {
                securityList: [
                    {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                ],
                subTypeList: [ SubType.SubType_OrderBook ],
                isSubOrUnSub: true,
                isRegOrUnRegPush: true, 
                },
            }).then((res) => { 

                const req = {
                    c2s: {
                        isReqAllConn: true,
                    },
                }; // 获取订阅状态参数

                websocket.GetSubInfo(req)
                .then((res) => { 
                    let { errCode, retMsg, retType,s2c } = res
                    if(retType == RetType.RetType_Succeed){
                        console.log("GetSubInfo: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                        console.log("GetSubInfo:", JSON.stringify(s2c)); 
                    } else {
                        console.log("GetSubInfo: error")
                    }
                })
                .catch((error) => {
                    console.log(error)
                    if ("retMsg" in error) {
                        console.log("error:", error.retMsg);
                    }
                });

            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
GetSubInfo: errCode 0, retMsg , retType 0
GetSubInfo: {"connSubInfoList":[{"subInfoList":[{"subType":2,"securityList":[{"market":1,"code":"00700"}]}],"usedQuota":1,"isOwnConnData":true}],"totalUsedQuota":1,"remainQuota":99}
stop
```

---

# 实时报价回调

`OnPush(cmd,res)`

* **介绍**

    实时报价回调，异步处理已订阅股票的实时报价推送。 

* **参数**
```protobuf

message S2C
{
	repeated Qot_Common.BasicQot basicQotList = 1; //股票基本行情
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType,返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 基础报价结构参见 [BasicQot](./quote.md#8209)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
function UpdateBasicQot(){
    const { RetType } = Common
    const { SubType, QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功
            const req = {
                c2s: {
                securityList: [
                    {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                ],
                subTypeList: [ SubType.SubType_Basic ], // 订阅实时报价类型
                isSubOrUnSub: true, // 订阅 true, 反订阅 false
                isRegOrUnRegPush: true, // 注册推送 true, 反注册推送 false
                },
            }; // 订阅参数

            websocket.Sub(req) //# 订阅, OpenD 开始持续收到服务器的推送
            .then((res) => { })
            .catch((error) => {
                if ("retMsg" in error) {
                    console.log("error:", error.retMsg);
                }
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.onPush = (cmd, res)=>{
        if(ftCmdID.QotUpdateBasicQot.cmd == cmd){ // 实时报价推送的处理逻辑
            let { retType, s2c } = res
            if(retType == RetType.RetType_Succeed){
                console.log("StockQuoteTest", JSON.stringify(s2c));
            } else {
                console.log("StockQuoteTest: error")
            }
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 接收 OpenD 的推送持续时间为5秒,5秒后断开
}
```

* **Output**

``` JavaScript
StockQuoteTest {"basicQotList":[{"security":{"market":1,"code":"00700"},"isSuspended":false,"listTime":"2004-06-16","priceSpread":0.2,"updateTime":"2021-09-09 16:08:17","highPrice":511.5,"openPrice":509,"lowPrice":479,"curPrice":480,"lastClosePrice":524.5,"volume":"54090872","turnover":26716845932,"turnoverRate":0.563,"amplitude":6.196,"darkStatus":0,"listTimestamp":1087315200,"updateTimestamp":1631174897,"secStatus":1}]}
StockQuoteTest { ... }
...
...
stop
```

:::tip 提示
* 此接口提供了持续获取推送数据的功能，如需一次性获取实时数据，请参考 [获取实时报价](./get-stock-quote.md) 接口
* 获取实时数据 和 实时数据回调 的差别，请参考 [如何通过订阅接口获取实时行情？](../qa/quote.md#2692)
:::

---

# 实时摆盘回调

`OnPush(cmd,res)`

* **介绍**

    实时摆盘回调，异步处理已订阅股票的实时摆盘推送。

* **参数**

```protobuf

message S2C
{
    required Qot_Common.Security security = 1; //股票
    optional string name = 8; //股票名称
    repeated Qot_Common.OrderBook orderBookAskList = 2; //卖盘
    repeated Qot_Common.OrderBook orderBookBidList = 3; //买盘
    optional string svrRecvTimeBid = 4; // 富途服务器从交易所收到数据的时间(for bid)部分数据的接收时间为零，例如服务器重启或第一次推送的缓存数据。该字段暂时只支持港股。
    optional double svrRecvTimeBidTimestamp = 5; // 富途服务器从交易所收到数据的时间戳(for bid)
    optional string svrRecvTimeAsk = 6; // 富途服务器从交易所收到数据的时间(for ask)
    optional double svrRecvTimeAskTimestamp = 7; // 富途服务器从交易所收到数据的时间戳(for ask)
    optional int32 orderBookType = 9; //Qot_Common.OrderBookType, 摆盘类型
}

message Response
{
    required int32 retType = 1 [default = -400]; //RetType，返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;

    optional S2C s2c = 4;
}
```
>   - 股票结构参见 [Security](./quote.md#1377)
>   - 买卖盘结构参见 [OrderBook](./quote.md#6364)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";

function UpdateOrderBook(){
    const { RetType } = Common
    const { SubType, QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功
            const req = {
                c2s: {
                securityList: [
                    {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                ],
                subTypeList: [ SubType.SubType_OrderBook ], // 订阅实时摆盘类型
                isSubOrUnSub: true, // 订阅 true, 反订阅 false
                isRegOrUnRegPush: true, // 注册推送 true, 反注册推送 false
                },
            }; // 订阅参数

            websocket.Sub(req) //# 订阅, OpenD 开始持续收到服务器的推送
            .then((res) => { })
            .catch((error) => {
                if ("retMsg" in error) {
                    console.log("error:", error.retMsg);
                }
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.onPush = (cmd, res)=>{
        if(ftCmdID.QotUpdateOrderBook.cmd == cmd){ // 实时摆盘推送的处理逻辑
            let { retType, s2c } = res
            if(retType == RetType.RetType_Succeed){
                console.log("OrderBookTest", JSON.stringify(s2c));
            } else {
                console.log("OrderBookTest: error")
            }
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 接收 OpenD 的推送持续时间为5秒,5秒后断开
}
```

* **Output**

``` JavaScript
OrderBookTest {"security":{"market":1,"code":"00700"},"orderBookAskList":[{"price":480.4,"volume":"700","orederCount":2},{"price":480.6,"volume":"385900","orederCount":14},{"price":480.8,"volume":"4200","orederCount":3},{"price":481,"volume":"15000","orederCount":14},{"price":481.2,"volume":"4600","orederCount":5},{"price":481.4,"volume":"13400","orederCount":4},{"price":481.6,"volume":"1800","orederCount":6},{"price":481.8,"volume":"3000","orederCount":8},{"price":482,"volume":"23700","orederCount":25},{"price":482.2,"volume":"1200","orederCount":3}],"orderBookBidList":[{"price":480,"volume":"55300","orederCount":39},{"price":479.8,"volume":"92400","orederCount":61},{"price":479.6,"volume":"106100","orederCount":41},{"price":479.4,"volume":"85900","orederCount":48},{"price":479.2,"volume":"78100","orederCount":34},{"price":479,"volume":"50200","orederCount":150},{"price":478.8,"volume":"51300","orederCount":44},{"price":478.6,"volume":"92700","orederCount":33},{"price":478.4,"volume":"5400","orederCount":16},{"price":478.2,"volume":"102500","orederCount":66}],"orderBookType":0}
OrderBookTest { ... }
 ...
 ...
stop
```

:::tip 提示
* 此接口提供了持续获取推送数据的功能，如需一次性获取实时数据，请参考 [获取实时摆盘](./get-order-book.md) 接口
* 获取实时数据 和 实时数据回调 的差别，请参考 [如何通过订阅接口获取实时行情？](../qa/quote.md#2692)
* 美股市场实时摆盘回调，会持续推送当前交易时段的实时摆盘，无需设置时段。
:::

---

# 实时 K 线回调

`OnPush(cmd,res)`

* **介绍**

    实时 K 线回调，异步处理已订阅股票的实时 K 线推送。

* **参数**

```protobuf
message S2C
{
	required int32 rehabType = 1; //Qot_Common.RehabType,复权类型
	required int32 klType = 2; //Qot_Common.KLType,K 线类型
	required Qot_Common.Security security = 3; //股票
    optional string name = 5; // 股票名称
	repeated Qot_Common.KLine klList = 4; //推送的 K 线数据结构体
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType,返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 股票结构参见[Security](./quote.md#1377)
>    - 复权类型参见[RehabType](./quote.md#6907)
>    - K 线类型参见[KLType](./quote.md#4119)
>    - K 线结构参见[KLine](./quote.md#5151)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";

function QotUpdateKL(){
    const { RetType } = Common
    const { SubType, QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功
            const req = {
                c2s: {
                securityList: [
                    {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                ],
                subTypeList: [ SubType.SubType_KL_1Min ], // 订阅实时K线(分K)类型
                isSubOrUnSub: true, // 订阅 true, 反订阅 false
                isRegOrUnRegPush: true, // 注册推送 true, 反注册推送 false
                },
            }; // 订阅参数

            websocket.Sub(req) //# 订阅, OpenD 开始持续收到服务器的推送
            .then((res) => { })
            .catch((error) => {
                if ("retMsg" in error) {
                    console.log("error:", error.retMsg);
                }
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.onPush = (cmd, res)=>{
        if(ftCmdID.QotUpdateKL.cmd == cmd){ // 实时K线推送的处理逻辑
            let { retType, s2c } = res
            if(retType == RetType.RetType_Succeed){
                console.log("CurKlineTest", JSON.stringify(s2c));
            } else {
                console.log("CurKlineTest: error")
            }
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 接收 OpenD 的推送持续时间为5秒,5秒后断开
}
```

* **Output**

``` JavaScript
CurKlineTest {"rehabType":1,"klType":1,"security":{"market":1,"code":"00700"},"klList":[{"time":"2021-09-09 16:00:00","isBlank":false,"highPrice":481.4,"openPrice":479.6,"lowPrice":479.6,"closePrice":480,"lastClosePrice":0,"volume":"5134400","turnover":2464740790,"turnoverRate":0,"pe":0,"timestamp":1631174400}]}
CurKlineTest { ... }
 ...
 ...
stop
```

:::tip 提示
* 此接口提供了持续获取推送数据的功能，如需一次性获取实时数据，请参考 [获取实时 K 线](./get-kl.md) 接口
* 获取实时数据 和 实时数据回调 的差别，请参考 [如何通过订阅接口获取实时行情？](../qa/quote.md#2692)
* **期权**，仅提供日K, 1分K，5分K，15分K，60分K。
:::

---

# 实时分时回调

`OnPush(cmd,res)`

* **介绍**

    实时分时回调，异步处理已订阅股票的实时分时推送。

* **参数**

```protobuf

message S2C
{
	required Qot_Common.Security security = 1; //股票
    optional string name = 3; //股票名称
	repeated Qot_Common.TimeShare rtList = 2; //推送的分时数据结构体
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType，返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 分时结构参见 [TimeShare](./quote.md#9906)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";

function QotUpdateRT(){
    const { RetType } = Common
    const { SubType, QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功
            const req = {
                c2s: {
                securityList: [
                    {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                ],
                subTypeList: [ SubType.SubType_RT ], // 订阅实时分时类型
                isSubOrUnSub: true, // 订阅 true, 反订阅 false
                isRegOrUnRegPush: true, // 注册推送 true, 反注册推送 false
                },
            }; // 订阅参数

            websocket.Sub(req) //# 订阅, OpenD 开始持续收到服务器的推送
            .then((res) => { })
            .catch((error) => {
                if ("retMsg" in error) {
                    console.log("error:", error.retMsg);
                }
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.onPush = (cmd, res)=>{
        if(ftCmdID.QotUpdateRT.cmd == cmd){ // 实时分时推送的处理逻辑
            let { retType, s2c } = res
            if(retType == RetType.RetType_Succeed){
                console.log("RTDataTest", JSON.stringify(s2c));
            } else {
                console.log("RTDataTest: error")
            }
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 接收 OpenD 的推送持续时间为5秒,5秒后断开
}
```

* **Output**

``` JavaScript
RTDataTest {"security":{"market":1,"code":"00700"},"rtList":[{"time":"2021-09-09 16:00:00","minute":960,"isBlank":false,"price":480,"lastClosePrice":524.5,"avgPrice":493.8398248240191,"volume":"5134400","turnover":2464740790,"timestamp":1631174400}]}
RTDataTest { ... }
 ...
 ...
stop
```

:::tip 提示
* 此接口提供了持续获取推送数据的功能，如需一次性获取实时数据，请参考 [获取实时分时](./get-rt.md) 接口
* 获取实时数据 和 实时数据回调 的差别，请参考 [如何通过订阅接口获取实时行情？](../qa/quote.md#2692)
:::

---

# 实时逐笔回调

`OnPush(cmd,res)`

* **介绍**

    实时逐笔回调，异步处理已订阅股票的实时逐笔推送。

* **参数**

```protobuf
message S2C
{
	required Qot_Common.Security security = 1; //股票
    optional string name = 3; //股票名称
	repeated Qot_Common.Ticker tickerList = 2; //推送的逐笔数据结构体
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType，返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 逐笔结构参见 [Ticker](./quote.md#9044)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";

function QotUpdateTicker(){
    const { RetType } = Common
    const { SubType, QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功
            const req = {
                c2s: {
                securityList: [
                    {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                ],
                subTypeList: [ SubType.SubType_Ticker ], // 订阅实时逐笔类型
                isSubOrUnSub: true, // 订阅 true, 反订阅 false
                isRegOrUnRegPush: true, // 注册推送 true, 反注册推送 false
                },
            }; // 订阅参数

            websocket.Sub(req) //# 订阅, OpenD 开始持续收到服务器的推送
            .then((res) => { })
            .catch((error) => {
                if ("retMsg" in error) {
                    console.log("error:", error.retMsg);
                }
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.onPush = (cmd, res)=>{
        if(ftCmdID.QotUpdateTicker.cmd == cmd){ // 实时逐笔推送的处理逻辑
            let { retType, s2c } = res
            if(retType == RetType.RetType_Succeed){
                console.log("TickerTest", JSON.stringify(s2c));
            } else {
                console.log("TickerTest: error")
            }
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 接收 OpenD 的推送持续时间为5秒,5秒后断开
}
```

* **Output**

``` JavaScript
TickerTest {"security":{"market":1,"code":"00700"},"tickerList":[{"time":"2021-09-09 16:08:12","sequence":"7005842815196387657","dir":3,"price":480,"volume":"4561200","turnover":2189376000,"recvTime":0,"type":7,"typeSign":85,"pushDataType":3,"timestamp":1631174892}]}
TickerTest { ... }
 ...
 ...
stop
```

:::tip 提示
* 此接口提供了持续获取推送数据的功能，如需一次性获取实时数据，请参考 [获取实时逐笔](./get-ticker.md) 接口
* 获取实时数据 和 实时数据回调 的差别，请参考 [如何通过订阅接口获取实时行情？](../qa/quote.md#2692)
* 行情连接断开重连后，OpenD 拉取断开期间，距离当前最近的（最多 50 根）逐笔数据并推送，可通过逐笔推送类型字段区分
:::

---

# 实时经纪队列回调

`OnPush(cmd,res)`

* **介绍**

    实时经纪队列回调，异步处理已订阅股票的实时经纪队列推送。

* **参数**

```protobuf
message S2C
{
	required Qot_Common.Security security = 1; //股票
    optional string name = 4; // 股票名称
	repeated Qot_Common.Broker brokerAskList = 2; //经纪 Ask(卖)盘
	repeated Qot_Common.Broker brokerBidList = 3; //经纪 Bid(买)盘
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType,返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 经纪队列结构参见 [Broker](./quote.md#4135)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";

function QotUpdateBroker(){
    const { RetType } = Common
    const { SubType, QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功
            const req = {
                c2s: {
                securityList: [
                    {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                ],
                subTypeList: [ SubType.SubType_Broker ], // 订阅实时经纪队列类型
                isSubOrUnSub: true, // 订阅 true, 反订阅 false
                isRegOrUnRegPush: true, // 注册推送 true, 反注册推送 false
                },
            }; // 订阅参数

            websocket.Sub(req) //# 订阅, OpenD 开始持续收到服务器的推送
            .then((res) => { })
            .catch((error) => {
                if ("retMsg" in error) {
                    console.log("error:", error.retMsg);
                }
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.onPush = (cmd, res)=>{
        if(ftCmdID.QotUpdateBroker.cmd == cmd){ // 实时经纪队列推送的处理逻辑
            let { retType, s2c } = res
            if(retType == RetType.RetType_Succeed){
                console.log("BrokerTest", JSON.stringify(s2c));
            } else {
                console.log("BrokerTest: error")
            }
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 接收 OpenD 的推送持续时间为5秒,5秒后断开
}
```

* **Output**

``` JavaScript
BrokerTest {"security":{"market":1,"code":"00700"},"brokerAskList":[{"id":"6429","name":"中信証券经纪(香港)有限公司","pos":1},{"id":"4973","name":"法国兴业证券(香港)有限公司","pos":1},{"id":"1175","name":"华泰金融控股(香港)有限公司","pos":2},{"id":"6389","name":"摩根士丹利","pos":2},{"id":"230","name":"立桥证券有限公司","pos":2},{"id":"9025","name":"瑞银","pos":2},{"id":"4098","name":"瑞士信贷证券(香港)有限公司","pos":2},{"id":"8734","name":"汇丰证券经纪(亚洲)有限公司","pos":2},{"id":"8308","name":"富途证券国际(香港)有限公司","pos":2},{"id":"3439","name":"高盛(亚洲)证券有限公司","pos":2},{"id":"8578","name":"汇丰证券经纪(亚洲)有限公司","pos":2},{"id":"3439","name":"高盛(亚洲)证券有限公司","pos":2},{"id":"3439","name":"高盛(亚洲)证券有限公司","pos":2},{"id":"3439","name":"高盛(亚洲)证券有限公司","pos":2},{"id":"8564","name":"荷银","pos":2},{"id":"8565","name":"荷银","pos":2},{"id":"8464","name":"富途证券国际(香港)有限公司","pos":3},{"id":"1174","name":"华泰金融控股(香港)有限公司","pos":3},{"id":"8578","name":"汇丰证券经纪(亚洲)有限公司","pos":3},{"id":"5666","name":"华侨永亨証券有限公司","pos":4},{"id":"6699","name":"盈透证券香港有限公司","pos":4},{"id":"4098","name":"瑞士信贷证券(香港)有限公司","pos":4},{"id":"4098","name":"瑞士信贷证券(香港)有限公司","pos":4},{"id":"4098","name":"瑞士信贷证券(香港)有限公司","pos":4},{"id":"6998","name":"中国投资信息有限公司","pos":4},{"id":"1292","name":"招银国际证券有限公司","pos":4},{"id":"1177","name":"华泰金融控股(香港)有限公司","pos":4},{"id":"6699","name":"盈透证券香港有限公司","pos":4},{"id":"6699","name":"盈透证券香港有限公司","pos":4},{"id":"1175","name":"华泰金融控股(香港)有限公司","pos":4},{"id":"6699","name":"盈透证券香港有限公司","pos":4},{"id":"6699","name":"盈透证券香港有限公司","pos":4},{"id":"6699","name":"盈透证券香港有限公司","pos":4},{"id":"6699","name":"盈透证券香港有限公司","pos":5},{"id":"6999","name":"中国投资信息有限公司","pos":5},{"id":"2310","name":"恒生证券有限公司","pos":5}],"brokerBidList":[{"id":"2846","name":"麦格理资本股份有限公司","pos":1},{"id":"8578","name":"汇丰证券经纪(亚洲)有限公司","pos":1},{"id":"6998","name":"中国投资信息有限公司","pos":1},{"id":"2847","name":"麦格理资本股份有限公司","pos":1},{"id":"6997","name":"中国投资信息有限公司","pos":1},{"id":"2847","name":"麦格理资本股份有限公司","pos":1},{"id":"6699","name":"盈透证券香港有限公司","pos":1},{"id":"2974","name":"星展唯高达香港有限公司","pos":1},{"id":"2847","name":"麦格理资本股份有限公司","pos":1},{"id":"1292","name":"招银国际证券有限公司","pos":1},{"id":"2846","name":"麦格理资本股份有限公司","pos":1},{"id":"8463","name":"富途证券国际(香港)有限公司","pos":1},{"id":"2846","name":"麦格理资本股份有限公司","pos":1},{"id":"5999","name":"中国创盈市场服务有限公司","pos":1},{"id":"5666","name":"华侨永亨証券有限公司","pos":1},{"id":"2847","name":"麦格理资本股份有限公司","pos":1},{"id":"5999","name":"中国创盈市场服务有限公司","pos":1},{"id":"5368","name":"星展唯高达香港有限公司","pos":1},{"id":"2846","name":"麦格理资本股份有限公司","pos":1},{"id":"1799","name":"耀才证券国际(香港)有限公司","pos":1},{"id":"690","name":"一通投资者有限公司","pos":1},{"id":"2847","name":"麦格理资本股份有限公司","pos":1},{"id":"229","name":"摩根士丹利","pos":1},{"id":"2846","name":"麦格理资本股份有限公司","pos":1},{"id":"8467","name":"富途证券国际(香港)有限公司","pos":1},{"id":"6996","name":"中国投资信息有限公司","pos":1},{"id":"2846","name":"麦格理资本股份有限公司","pos":1},{"id":"8574","name":"汇丰证券经纪(亚洲)有限公司","pos":1},{"id":"3643","name":"美林","pos":1},{"id":"6721","name":"宝生证券及期货有限公司","pos":1},{"id":"6727","name":"宝生证券及期货有限公司","pos":1},{"id":"2846","name":"麦格理资本股份有限公司","pos":1},{"id":"5999","name":"中国创盈市场服务有限公司","pos":1},{"id":"9139","name":"实德证券有限公司","pos":1},{"id":"2026","name":"东亚证券有限公司","pos":1},{"id":"1978","name":"哈富证券有限公司","pos":1},{"id":"2846","name":"麦格理资本股份有限公司","pos":1},{"id":"1799","name":"耀才证券国际(香港)有限公司","pos":1},{"id":"2245","name":"富途证券国际(香港)有限公司","pos":1}]}
BrokerTest { ... }
 ...
 ...
stop
```

:::tip 提示
* 此接口提供了持续获取推送数据的功能，如需一次性获取实时数据，请参考 [获取实时经纪队列](./get-broker.md) 接口
* 获取实时数据 和 实时数据回调 的差别，请参考 [如何通过订阅接口获取实时行情？](../qa/quote.md#2692)
* 港股 BMP及LV1 权限下，不支持获取经纪队列数据
:::

---

# 获取快照

`GetSecuritySnapshot(req);`

* **介绍**

    获取快照数据

* **参数**

```protobuf
message C2S
{
	repeated Qot_Common.Security securityList = 1; //股票
	optional Qot_Common.QotHeader header = 100; //行情公共参数头
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 行情公共参数头结构参见 [QotHeader](./quote.md#6938)

* **返回**

```protobuf
 // 正股类型额外数据
message EquitySnapshotExData
{
    required int64 issuedShares = 1; // 总股本
	required double issuedMarketVal = 2; // 总市值 =总股本*当前价格
    required double netAsset = 3; // 资产净值
    required double netProfit = 4; // 盈利（亏损）
    required double earningsPershare = 5; // 每股盈利
    required int64 outstandingShares = 6; // 流通股本
	required double outstandingMarketVal = 7; // 流通市值 =流通股本*当前价格
    required double netAssetPershare = 8; // 每股净资产
    required double eyRate = 9; // 收益率（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
    required double peRate = 10; // 市盈率
    required double pbRate = 11; // 市净率
	required double peTTMRate = 12; // 市盈率 TTM
	optional double dividendTTM = 13; // 股息 TTM，派息
    optional double dividendRatioTTM = 14; // 股息率 TTM（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
	optional double dividendLFY = 15; // 股息 LFY，上一年度派息
    optional double dividendLFYRatio = 16; // 股息率 LFY（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
}

 // 窝轮类型额外数据
message WarrantSnapshotExData
{
    required double conversionRate = 1; //换股比率
    required int32 warrantType = 2; //Qot_Common.WarrantType，窝轮类型
    required double strikePrice = 3; //行使价
    required string maturityTime = 4; //到期日时间字符串
    required string endTradeTime = 5; //最后交易日时间字符串
    required Qot_Common.Security owner = 6; //所属正股 
    required double recoveryPrice = 7; //收回价，仅牛熊证支持该字段
    required int64 streetVolumn = 8; //街货量
    required int64 issueVolumn = 9; //发行量
    required double streetRate = 10; //街货占比（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
    required double delta = 11; //对冲值，仅认购认沽支持该字段
    required double impliedVolatility = 12; //引申波幅，仅认购认沽支持该字段
    required double premium = 13; //溢价（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
    optional double maturityTimestamp = 14; //到期日时间戳
    optional double endTradeTimestamp = 15; //最后交易日时间戳
    optional double leverage = 16;  // 杠杆比率（倍）
    optional double ipop = 17; // 价内/价外（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
    optional double breakEvenPoint = 18; // 打和点
    optional double conversionPrice = 19;  // 换股价
    optional double priceRecoveryRatio = 20; // 正股距收回价（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
    optional double score = 21; // 综合评分
    optional double upperStrikePrice = 22; //上限价，仅界内证支持该字段
    optional double lowerStrikePrice = 23; //下限价，仅界内证支持该字段
    optional int32 inLinePriceStatus = 24; //Qot_Common.PriceType，界内界外，仅界内证支持该字段
    optional string issuerCode = 25; //发行人代码
}

 // 期权类型额外数据
message OptionSnapshotExData
{
	required int32 type = 1; //Qot_Common.OptionType，期权类型（按方向）
	required Qot_Common.Security owner = 2; //标的股
	required string strikeTime = 3; //行权日时间字符串（格式：yyyy-MM-dd）
    required double strikePrice = 4; //行权价
	required int32 contractSize = 5; //每份合约数(整型数据)
	optional double contractSizeFloat = 22; //每份合约数（浮点型数据）
	required int32 openInterest = 6; //未平仓合约数
	required double impliedVolatility = 7; //隐含波动率（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
	required double premium = 8; //溢价（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
	required double delta = 9; //希腊值 Delta
    required double gamma = 10; //希腊值 Gamma
	required double vega = 11; //希腊值 Vega
    required double theta = 12; //希腊值 Theta
    required double rho = 13; //希腊值 Rho
	optional double strikeTimestamp = 14; //行权日时间戳  
	optional int32 indexOptionType = 15; //Qot_Common.IndexOptionType，指数期权类型
	optional int32 netOpenInterest = 16; //净未平仓合约数，仅港股期权适用	
	optional int32 expiryDateDistance = 17; //距离到期日天数，负数表示已过期
	optional double contractNominalValue = 18; //合约名义金额，仅港股期权适用
	optional double ownerLotMultiplier = 19; //相等正股手数，指数期权无该字段，仅港股期权适用
	optional int32 optionAreaType = 20; //Qot_Common.OptionAreaType，期权类型（按行权时间）
	optional double contractMultiplier = 21; //合约乘数
}

// 指数类型额外数据
message IndexSnapshotExData
{
    required int32 raiseCount = 1;  // 上涨支数
    required int32 fallCount = 2;  // 下跌支数
    required int32 equalCount = 3;  // 平盘支数
}

// 板块类型额外数据
message PlateSnapshotExData
{
    required int32 raiseCount = 1;  // 上涨支数
    required int32 fallCount = 2;  // 下跌支数
    required int32 equalCount = 3;  // 平盘支数
}

//期货类型额外数据
message FutureSnapshotExData
{
	required double lastSettlePrice = 1; //昨结
	required int32 position = 2; //持仓量
	required int32 positionChange = 3; //日增仓
	required string lastTradeTime = 4; //最后交易日，只有非主连期货合约才有该字段
	optional double lastTradeTimestamp = 5; //最后交易日时间戳，只有非主连期货合约才有该字段
	required bool isMainContract = 6; //是否主连合约
}

//基金类型额外数据
message TrustSnapshotExData
{
	required double dividendYield = 1; //股息率（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
	required double aum = 2; //资产规模
	required int64 outstandingUnits = 3; //总发行量
	required double netAssetValue = 4; //单位净值
	required double premium = 5; //溢价（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
	required int32 assetClass = 6; //Qot_Common.AssetClass，资产类别
}

 //基本快照数据
message SnapshotBasicData
{
	required Qot_Common.Security security = 1; //证券
    optional string name = 41; //股票名称
	required int32 type = 2; //Qot_Common.SecurityType，证券类型
	required bool isSuspend = 3; //是否停牌
	required string listTime = 4; //上市时间字符串（格式：yyyy-MM-dd）
	required int32 lotSize = 5; //每手数量
	required double priceSpread = 6; //价差
	required string updateTime = 7; //更新时间字符串（格式：yyyy-MM-dd HH:mm:ss）
	required double highPrice = 8; //最高价
	required double openPrice = 9; //开盘价
	required double lowPrice = 10; //最低价
	required double lastClosePrice = 11; //昨收价
	required double curPrice = 12; //最新价
	required int64 volume = 13; //成交量
	required double turnover = 14; //成交额
	required double turnoverRate = 15; //换手率（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
	optional double listTimestamp = 16; //上市时间戳
	optional double updateTimestamp = 17; //更新时间戳
	optional double askPrice = 18;//卖价
    optional double bidPrice = 19;//买价
	optional int64 askVol = 20;//卖量
    optional int64 bidVol = 21;//买量
	optional bool enableMargin = 22; // 是否可融资（已废弃，请使用 获取融资融券数据 接口获取）
    optional double mortgageRatio = 23; // 股票抵押率（已废弃，请使用 获取融资融券数据 接口获取）
    optional double longMarginInitialRatio = 24; // 融资初始保证金率（已废弃，请使用 获取融资融券数据 接口获取）
    optional bool enableShortSell = 25; // 是否可卖空（已废弃，请使用 获取融资融券数据 接口获取）
    optional double shortSellRate = 26; // 卖空参考利率（已废弃，请使用 获取融资融券数据 接口获取）
    optional int64 shortAvailableVolume = 27; // 剩余可卖空数量（已废弃，请使用 获取融资融券数据 接口获取）
    optional double shortMarginInitialRatio = 28; // 卖空（融券）初始保证金率（已废弃，请使用 获取融资融券数据 接口获取）
	optional double amplitude = 29; // 振幅（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
	optional double avgPrice = 30; // 平均价
	optional double bidAskRatio = 31; // 委比（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
	optional double volumeRatio = 32;  // 量比
	optional double highest52WeeksPrice = 33;  // 52周最高价
    optional double lowest52WeeksPrice = 34;  // 52周最低价
	optional double highestHistoryPrice = 35;  // 历史最高价
    optional double lowestHistoryPrice = 36;  // 历史最低价
	optional Qot_Common.PreAfterMarketData preMarket = 37; //Qot_Common::PreAfterMarketData 盘前数据
	optional Qot_Common.PreAfterMarketData afterMarket = 38; //Qot_Common::PreAfterMarketData 
    optional Qot_Common.PreAfterMarketData overnight = 42; //Qot_Common::PreAfterMarketData 夜盘数据
	optional int32 secStatus = 39; //Qot_Common::SecurityStatus 股票状态
	optional double closePrice5Minute = 40; //5分钟收盘价
	optional double hpVolume = 43; //高精度成交量
	optional double hpAskVol = 44; //高精度卖量
	optional double hpBidVol = 45; //高精度买量
}

message Snapshot
{
	required SnapshotBasicData basic = 1; //快照基本数据
	optional EquitySnapshotExData equityExData = 2; //正股快照额外数据
	optional WarrantSnapshotExData warrantExData = 3; //窝轮快照额外数据
	optional OptionSnapshotExData optionExData = 4; //期权快照额外数据
	optional IndexSnapshotExData indexExData = 5; //指数快照额外数据
	optional PlateSnapshotExData plateExData = 6; //板块快照额外数据
	optional FutureSnapshotExData futureExData = 7; //期货类型额外数据
	optional TrustSnapshotExData trustExData = 8; //基金类型额外数据
}

message S2C
{
	repeated Snapshot snapshotList = 1; //股票快照
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType，返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetSecuritySnapshot(){
    const { RetType } = Common
    const { SubType, QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功

            const req = {
                c2s: {
                securityList: [
                    {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                ],
                },
            };
            websocket.GetSecuritySnapshot(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("Snapshot: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                if(retType == RetType.RetType_Succeed){
                    let snapshot = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(snapshot);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
Snapshot: errCode 0, retMsg , retType 0
{
  "snapshotList": [{
    "basic": {
      "security": {
        "market": 1,
        "code": "00700"
      },
      "type": 3,
      "isSuspend": false,
      "listTime": "2004-06-16",
      "lotSize": 100,
      "priceSpread": 0.2,
      "updateTime": "2021-09-09 16:08:17",
      "highPrice": 511.5,
      "openPrice": 509,
      "lowPrice": 479,
      "lastClosePrice": 524.5,
      "curPrice": 480,
      "volume": "54090872",
      "turnover": 26716845932,
      "turnoverRate": 0.563,
      "listTimestamp": 1087315200,
      "updateTimestamp": 1631174897,
      "askPrice": 480.4,
      "bidPrice": 480,
      "askVol": "700",
      "bidVol": "55300",
      "enableMargin": true,
      "mortgageRatio": 0,
      "longMarginInitialRatio": 35,
      "enableShortSell": true,
      "shortSellRate": 0.92,
      "shortAvailableVolume": "3059000",
      "shortMarginInitialRatio": 50,
      "amplitude": 6.196,
      "avgPrice": 493.925,
      "bidAskRatio": 22.703,
      "volumeRatio": 1.775,
      "highest52WeeksPrice": 773.9,
      "lowest52WeeksPrice": 412.2,
      "highestHistoryPrice": 773.9,
      "lowestHistoryPrice": -6.381,
      "secStatus": 1,
      "closePrice5Minute": 483.4
    },
    "equityExData": {
      "issuedShares": "9599810645",
      "issuedMarketVal": 4607909109600,
      "netAsset": 1016063158288.09,
      "netProfit": 190383444711.64,
      "earningsPershare": 19.832,
      "outstandingShares": "9599810645",
      "outstandingMarketVal": 4607909109600,
      "netAssetPershare": 105.842,
      "eyRate": 0.22,
      "peRate": 24.203,
      "pbRate": 4.535,
      "peTTMRate": 20.532,
      "dividendTTM": 1.599,
      "dividendRatioTTM": 0.33,
      "dividendLFY": 1.599,
      "dividendLFYRatio": 0.333
    }
  }]
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 60 次快照。
* 每次请求，接口参数 **股票代码列表** 支持传入的标的数量上限是 400 个。
* 港股 BMP 权限下，单次请求的香港证券（含窝轮、牛熊、界内证）快照数量上限是 20 个。
* 港股期权期货 BMP 权限下，单次请求的香港期货和期权的快照数量上限是 20 个。
:::

---

# 获取实时报价

`GetBasicQot(req);`

* **介绍**

    获取已订阅股票的实时报价，必须要先订阅。

* **参数**

```protobuf
message C2S
{
	repeated Qot_Common.Security securityList = 1; //股票
	optional Qot_Common.QotHeader header = 100; //行情公共参数头
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 行情公共参数头结构参见 [QotHeader](./quote.md#6938)

* **返回**

```protobuf
message S2C
{
	repeated Qot_Common.BasicQot basicQotList = 1; //股票基本行情
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType，返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 基础报价结构参见 [BasicQot](./quote.md#8209)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetBasicQot(){
    const { RetType } = Common
    const { SubType, QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功
            websocket.Sub({
                c2s: {
                securityList: [
                    {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                ],
                subTypeList: [ SubType.SubType_Basic ], // 订阅实时报价类型
                isSubOrUnSub: true, // 订阅 true, 反订阅 false
                isRegOrUnRegPush: true, // 注册推送 true, 反注册推送 false
                },
            })
            .then((res) => { 

                const req = {
                    c2s: {
                    securityList: [
                        {
                            market: QotMarket.QotMarket_HK_Security,
                            code: "00700",
                        },
                    ],
                    },
                };
                websocket.GetBasicQot(req)
                .then((res) => {
                    let { errCode, retMsg, retType,s2c } = res
                    console.log("BasicQot: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                    if(retType == RetType.RetType_Succeed){
                        let s2c = beautify(JSON.stringify(s2c), {
                            indent_size: 2,
                            space_in_empty_paren: true,
                        });
                        console.log(s2c);
                    }
                })
                .catch((error) => {
                    console.log("error:", error);
                });

            })
            .catch((error) => {
                if ("retMsg" in error) {
                    console.log("error:", error.retMsg);
                }
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
BasicQot: errCode 0, retMsg , retType 0
{
  "basicQotList": [{
    "security": {
      "market": 1,
      "code": "00700"
    },
    "isSuspended": false,
    "listTime": "2004-06-16",
    "priceSpread": 0.2,
    "updateTime": "2021-09-09 16:08:17",
    "highPrice": 511.5,
    "openPrice": 509,
    "lowPrice": 479,
    "curPrice": 480,
    "lastClosePrice": 524.5,
    "volume": "54090872",
    "turnover": 26716845932,
    "turnoverRate": 0.563,
    "amplitude": 6.196,
    "darkStatus": 0,
    "listTimestamp": 1087315200,
    "updateTimestamp": 1631174897,
    "secStatus": 1
  }]
}
stop
```

:::tip 提示
* 此接口提供了一次性获取实时数据的功能，如需持续获取推送数据，请参考 [实时报价回调](./update-stock-quote.md) 接口
* 获取实时数据 和 实时数据回调 的差别，请参考 [如何通过订阅接口获取实时行情？](../qa/quote.md#2692)
:::

---

# 获取实时摆盘

`GetOrderBook(req);`

* **介绍**

    获取已订阅股票的实时摆盘，必须要先订阅。

* **参数**

```protobuf
message C2S
{
	required Qot_Common.Security security = 1; //股票
	required int32 num = 2; //请求的摆盘个数
	optional int32 orderBookType = 4; //Qot_Common.OrderBookType, 摆盘类型，不传默认返回整股盘
	optional Qot_Common.QotHeader header = 100; //行情公共参数头
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 行情公共参数头结构参见 [QotHeader](./quote.md#6938)

* **返回**

```protobuf
message S2C
{
	required Qot_Common.Security security = 1; //股票
    optional string name = 8; //股票名称
	repeated Qot_Common.OrderBook orderBookAskList = 2; //卖盘
	repeated Qot_Common.OrderBook orderBookBidList = 3; //买盘
	optional string svrRecvTimeBid = 4; // 富途服务器从交易所收到数据的时间(for bid)部分数据的接收时间为零，例如服务器重启或第一次推送的缓存数据。该字段暂时只支持港股。
	optional double svrRecvTimeBidTimestamp = 5; // 富途服务器从交易所收到数据的时间戳(for bid)
	optional string svrRecvTimeAsk = 6; // 富途服务器从交易所收到数据的时间(for ask)
	optional double svrRecvTimeAskTimestamp = 7; // 富途服务器从交易所收到数据的时间戳(for ask)
	optional int32 orderBookType = 9; //Qot_Common.OrderBookType, 摆盘类型
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType，返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	optional S2C s2c = 4;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 买卖盘结构参见 [OrderBook](./quote.md#6364)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetOrderBook(){
    const { RetType } = Common
    const { SubType, QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功
            websocket.Sub({
                c2s: {
                securityList: [
                    {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                ],
                subTypeList: [ SubType.SubType_OrderBook ], // 订阅实时摆盘类型
                isSubOrUnSub: true, // 订阅 true, 反订阅 false
                isRegOrUnRegPush: true, // 注册推送 true, 反注册推送 false
                },
            })
            .then((res) => { 

                const req = {
                    c2s: {
                        security: {
                            market: QotMarket.QotMarket_HK_Security,
                            code: "00700",
                        },
                        num: 2,
                    },
                };
                websocket.GetOrderBook(req)
                .then((res) => {
                    let { errCode, retMsg, retType,s2c } = res
                    console.log("OrderBook: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                    if(retType == RetType.RetType_Succeed){
                        let data = beautify(JSON.stringify(s2c), {
                            indent_size: 2,
                            space_in_empty_paren: true,
                        });
                        console.log(data);
                    }
                })
                .catch((error) => {
                    console.log("getorderbook error:", error);
                });

            })
            .catch((error) => {
                if ("retMsg" in error) {
                    console.log("sub error:", error.retMsg);
                }
            });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
OrderBook: errCode 0, retMsg , retType 0
{
  "security": {
    "market": 1,
    "code": "00700"
  },
  "orderBookAskList": [{
    "price": 480.4,
    "volume": "700",
    "orederCount": 2
  }, {
    "price": 480.6,
    "volume": "385900",
    "orederCount": 14
  }],
  "orderBookBidList": [{
    "price": 480,
    "volume": "55300",
    "orederCount": 39
  }, {
    "price": 479.8,
    "volume": "92400",
    "orederCount": 61
  }],
  "orderBookType": 0
}
stop
```

:::tip 接口限制
* 富途服务器从交易所收到数据的时间字段，仅支持A股正股、港股正股、ETFs、窝轮、牛熊，且仅开盘时间才有此数据。
* 富途服务器从交易所收到数据的时间字段，部分情况下接收时间可能为零，例如：服务器重启或第一次推送的缓存数据。
:::

:::tip 提示
* 此接口提供了一次性获取实时数据的功能，如需持续获取推送数据，请参考 [实时摆盘回调](./update-order-book.md) 接口
* 获取实时数据 和 实时数据回调 的差别，请参考 [如何通过订阅接口获取实时行情？](../qa/quote.md#2692)
* 美股市场，会返回当前交易时段的实时摆盘数据，无需设置时段。
:::

---

# 获取实时 K 线

`GetKL(req);`

* **介绍**

    获取已订阅股票的实时 K 线数据，必须要先订阅。

* **参数**

```protobuf
message C2S
{
	required int32 rehabType = 1; //Qot_Common.RehabType，复权类型
	required int32 klType = 2; //Qot_Common.KLType，K 线时间周期
	required Qot_Common.Security security = 3; //股票
	required int32 reqNum = 4; //请求 K 线根数
	optional Qot_Common.QotHeader header = 100; //行情公共参数头
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 复权类型参见 [RehabType](./quote.md#6907)
>    - K 线类型参见 [KLType](./quote.md#4119)
>    - 行情公共参数头结构参见 [QotHeader](./quote.md#6938)

* **返回**

```protobuf
message S2C
{
	required Qot_Common.Security security = 1; //股票
    optional string name = 3; // 股票名称
	repeated Qot_Common.KLine klList = 2; //K 线数据结构体
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType,返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;

	optional S2C s2c = 4;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - K 线结构参见 [KLine](./quote.md#5151)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetKL(){
    const { RetType } = Common
    const { SubType, QotMarket, RehabType, KLType } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();
    
    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功
            websocket.Sub({
                c2s: {
                securityList: [
                    {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                ],
                subTypeList: [ SubType.SubType_KL_1Min ], // 订阅实时K线(分K)类型
                isSubOrUnSub: true, // 订阅 true, 反订阅 false
                isRegOrUnRegPush: true, // 注册推送 true, 反注册推送 false
                },
            })
            .then((res) => { 

                const req = {
                    c2s: {
                        rehabType: RehabType.RehabType_Forward,
                        klType: KLType.KLType_1Min,
                        security: {
                            market: QotMarket.QotMarket_HK_Security,
                            code: "00700",
                        },
                        reqNum: 2,
                    },
                };
                
                websocket.GetKL(req)
                .then((res) => {
                    let { errCode, retMsg, retType,s2c } = res
                    console.log("KL: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                    if(retType == RetType.RetType_Succeed){
                        let data = beautify(JSON.stringify(s2c), {
                            indent_size: 2,
                            space_in_empty_paren: true,
                        });
                        console.log(data);
                    }
                })
                .catch((error) => {
                    console.log("error:", error);
                });

            })
            .catch((error) => {
                if ("retMsg" in error) {
                    console.log("sub error:", error.retMsg);
                }
            });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
KL: errCode 0, retMsg , retType 0
{
  "security": {
    "market": 1,
    "code": "00700"
  },
  "klList": [{
    "time": "2021-09-09 15:59:00",
    "isBlank": false,
    "highPrice": 480.4,
    "openPrice": 480.2,
    "lowPrice": 479,
    "closePrice": 479.6,
    "lastClosePrice": 480.2,
    "volume": "1326900",
    "turnover": 636738960,
    "turnoverRate": 0,
    "pe": 0,
    "changeRate": -0.12494793835900997,
    "timestamp": 1631174340
  }, {
    "time": "2021-09-09 16:00:00",
    "isBlank": false,
    "highPrice": 481.4,
    "openPrice": 479.6,
    "lowPrice": 479.6,
    "closePrice": 480,
    "lastClosePrice": 479.6,
    "volume": "5134400",
    "turnover": 2464740790,
    "turnoverRate": 0,
    "pe": 0,
    "changeRate": 0.08340283569640894,
    "timestamp": 1631174400
  }]
}
stop
```

:::tip 接口限制
* 此接口为获取实时 K 线接口，最多能获取最近的 1000 根。如需获取历史 K 线，请参考 [获取历史 K 线](../quote/request-history-kline.md)
* 市盈率和换手率字段，只有日 K 及以上周期的正股才有数据
* **期权**，仅提供日K, 1分K，5分K，15分K，60分K。
:::

:::tip 提示
* 此接口提供了一次性获取实时数据的功能，如需持续获取推送数据，请参考 [实时 K 线回调](./update-kl.md) 接口
* 获取实时数据 和 实时数据回调 的差别，请参考 [如何通过订阅接口获取实时行情？](../qa/quote.md#2692)
:::

---

# 获取实时分时

`GetRT(req);`

* **介绍**

    获取已订阅股票的实时分时数据，必须要先订阅。

* **参数**

```protobuf
message C2S
{
	required Qot_Common.Security security = 1; //股票
	optional Qot_Common.QotHeader header = 100; //行情公共参数头
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 行情公共参数头结构参见 [QotHeader](./quote.md#6938)

* **返回**

```protobuf
message S2C
{
	required Qot_Common.Security security = 1; //股票
    optional string name = 3; //股票名称
	repeated Qot_Common.TimeShare rtList = 2; //分时数据结构体
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType，返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 分时结构参见 [TimeShare](./quote.md#9906)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetRT(){
    const { RetType } = Common
    const { SubType, QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();
    
    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功
            websocket.Sub({
                c2s: {
                securityList: [
                    {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                ],
                subTypeList: [ SubType.SubType_RT ], // 订阅实时分时类型
                isSubOrUnSub: true, // 订阅 true, 反订阅 false
                isRegOrUnRegPush: true, // 注册推送 true, 反注册推送 false
                },
            })
            .then((res) => { 

                const req = {
                    c2s: {
                        security: {
                            market: QotMarket.QotMarket_HK_Security,
                            code: "00700",
                        },
                    },
                };
                
                websocket.GetRT(req)
                .then((res) => {
                    let { errCode, retMsg, retType,s2c } = res
                    console.log("RT: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                    if(retType == RetType.RetType_Succeed){
                        let data = beautify(JSON.stringify(s2c), {
                            indent_size: 2,
                            space_in_empty_paren: true,
                        });
                        console.log(data);
                    }
                })
                .catch((error) => {
                    console.log("error:", error);
                });

            })
            .catch((error) => {
                if ("retMsg" in error) {
                    console.log("sub error:", error.retMsg);
                }
            });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
RT: errCode 0, retMsg , retType 0
{
  "security": {
    "market": 1,
    "code": "00700"
  },
  "rtList": [{
    "time": "2021-09-09 09:30:00",
    "minute": 570,
    "isBlank": false,
    "price": 509,
    "lastClosePrice": 524.5,
    "avgPrice": 509,
    "volume": "941800",
    "turnover": 479376200,
    "timestamp": 1631151000
  }, {
    "time": "2021-09-09 09:31:00",
    "minute": 571,
    "isBlank": false,
    "price": 506.5,
    "lastClosePrice": 524.5,
    "avgPrice": 507.88588572919383,
    "volume": "974700",
    "turnover": 493987100,
    "timestamp": 1631151060
  }, ..., {
    "time": "2021-09-09 09:32:00",
    "minute": 572,
    "isBlank": false,
    "price": 504,
    "lastClosePrice": 524.5,
    "avgPrice": 507.3999031165602,
    "volume": "416200",
    "turnover": 210248454,
    "timestamp": 1631151120
  },],
}
stop
```

:::tip 提示
* 此接口提供了一次性获取实时数据的功能，如需持续获取推送数据，请参考 [实时分时回调](./update-rt.md) 接口
* 获取实时数据 和 实时数据回调 的差别，请参考 [如何通过订阅接口获取实时行情？](../qa/quote.md#2692)
:::

---

# 获取实时逐笔

`GetTicker(req);`

* **介绍**

    获取指定股票的实时逐笔，需要先订阅。

* **参数**

```protobuf
message C2S
{
	required Qot_Common.Security security = 1; //股票
	required int32 maxRetNum = 2; //最多返回的逐笔个数，实际返回数量不一定会返回这么多，最多返回1000个
	optional Qot_Common.QotHeader header = 100; //行情公共参数头
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 行情公共参数头结构参见 [QotHeader](./quote.md#6938)

* **返回**

```protobuf
message S2C
{
    required Qot_Common.Security security = 1; //股票
    optional string name = 3; // 股票名称
	repeated Qot_Common.Ticker tickerList = 2; //逐笔数据结构体
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType,返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	optional S2C s2c = 4;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 逐笔结构参见 [Ticker](./quote.md#9044)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetTicker(){
    const { RetType } = Common
    const { SubType, QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();
    
    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功
            websocket.Sub({
                c2s: {
                securityList: [
                    {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                ],
                subTypeList: [ SubType.SubType_Ticker ], // 订阅实时逐笔类型
                isSubOrUnSub: true, // 订阅 true, 反订阅 false
                isRegOrUnRegPush: true, // 注册推送 true, 反注册推送 false
                },
            })
            .then((res) => { 

                const req = {
                    c2s: {
                        security: {
                            market: QotMarket.QotMarket_HK_Security,
                            code: "00700",
                        },
                        maxRetNum: 3,
                    },
                };
                
                websocket.GetTicker(req)
                .then((res) => {
                    let { errCode, retMsg, retType,s2c } = res
                    console.log("Ticker: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                    if(retType == RetType.RetType_Succeed){
                        let data = beautify(JSON.stringify(s2c), {
                            indent_size: 2,
                            space_in_empty_paren: true,
                        });
                        console.log(data);
                    }
                })
                .catch((error) => {
                    console.log("error:", error);
                });

            })
            .catch((error) => {
                if ("retMsg" in error) {
                    console.log("sub error:", error.retMsg);
                }
            });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
Ticker: errCode 0, retMsg , retType 0
{
  "security": {
    "market": 1,
    "code": "00700"
  },
  "tickerList": [{
    "time": "2021-09-09 15:59:59",
    "sequence": "7005840697777510727",
    "dir": 2,
    "price": 481.2,
    "volume": "100",
    "turnover": 48120,
    "recvTime": 0,
    "type": 1,
    "typeSign": 32,
    "timestamp": 1631174399
  }, {
    "time": "2021-09-09 16:05:24",
    "sequence": "7005842093641881928",
    "dir": 3,
    "price": 476,
    "volume": "42",
    "turnover": 19992,
    "recvTime": 0,
    "type": 6,
    "typeSign": 68,
    "timestamp": 1631174724
  }, {
    "time": "2021-09-09 16:08:12",
    "sequence": "7005842815196387657",
    "dir": 3,
    "price": 480,
    "volume": "4561200",
    "turnover": 2189376000,
    "recvTime": 0,
    "type": 7,
    "typeSign": 85,
    "timestamp": 1631174892
  }]
}
stop
```

:::tip 接口限制
* 最多能获取最近 1000 个逐笔数据，更多历史逐笔数据暂未提供
* 港股期权期货在 LV1 权限下，不支持获取逐笔
:::

:::tip 提示
* 此接口提供了一次性获取实时数据的功能，如需持续获取推送数据，请参考 [实时逐笔回调](./update-ticker.md) 接口
* 获取实时数据 和 实时数据回调 的差别，请参考 [如何通过订阅接口获取实时行情？](../qa/quote.md#2692)
:::

---

# 获取实时经纪队列

`GetBroker(req);`

* **介绍**

    获取已订阅股票的实时报价，必须要先订阅。

* **参数**

```protobuf
message C2S
{
	required Qot_Common.Security security = 1; //股票
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)

* **返回**

```protobuf
message S2C
{
	required Qot_Common.Security security = 1; //股票
	optional string name = 4; // 股票名称
    repeated Qot_Common.Broker brokerAskList = 2; //经纪 Ask(卖)盘
	repeated Qot_Common.Broker brokerBidList = 3; //经纪 Bid(买)盘
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType,返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	optional S2C s2c = 4;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 经纪队列结构参见 [Broker](./quote.md#4135)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetBroker(){
    const { RetType } = Common
    const { SubType, QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();
    
    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功
            websocket.Sub({
                c2s: {
                securityList: [
                    {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                ],
                subTypeList: [ SubType.SubType_Broker ], // 订阅实时经纪队列类型
                isSubOrUnSub: true, // 订阅 true, 反订阅 false
                isRegOrUnRegPush: true, // 注册推送 true, 反注册推送 false
                },
            })
            .then((res) => { 

                const req = {
                    c2s: {
                        security: {
                            market: QotMarket.QotMarket_HK_Security,
                            code: "00700",
                        },
                    },
                };
                
                websocket.GetBroker(req)
                .then((res) => {
                    let { errCode, retMsg, retType,s2c } = res
                    console.log("Broker: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                    if(retType == RetType.RetType_Succeed){
                        let data = beautify(JSON.stringify(s2c), {
                            indent_size: 2,
                            space_in_empty_paren: true,
                        });
                        console.log(data);
                    }
                })
                .catch((error) => {
                    console.log("error:", error);
                });

            })
            .catch((error) => {
                if ("retMsg" in error) {
                    console.log("sub error:", error.retMsg);
                }
            });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
Broker: errCode 0, retMsg , retType 0
{
  "security": {
    "market": 1,
    "code": "00700"
  },
  "brokerAskList": [{
    "id": "6429",
    "name": "中信証券经纪(香港)有限公司",
    "pos": 1
  }, {
    "id": "4973",
    "name": "法国兴业证券(香港)有限公司",
    "pos": 1
  }, ..., {
    "id": "2310",
    "name": "恒生证券有限公司",
    "pos": 5
  }],
  "brokerBidList": [{
    "id": "2846",
    "name": "麦格理资本股份有限公司",
    "pos": 1
  }, {
    "id": "8578",
    "name": "汇丰证券经纪(亚洲)有限公司",
    "pos": 1
  }, ..., {
    "id": "2245",
    "name": "富途证券国际(香港)有限公司",
    "pos": 1
  }]
}
stop
```

:::tip 提示
* 此接口提供了一次性获取实时数据的功能，如需持续获取推送数据，请参考 [实时经纪队列回调](./update-broker.md) 接口
* 获取实时数据 和 实时数据回调 的差别，请参考 [如何通过订阅接口获取实时行情？](../qa/quote.md#2692)
* 港股 BMP及LV1 权限下，不支持获取经纪队列数据
:::

---

# 获取标的市场状态

`GetMarketState(req);`

* **介绍**

    获取指定标的的市场状态

* **参数**

```protobuf
message C2S
{
	repeated Qot_Common.Security securityList = 1; //股票列表
	optional Qot_Common.QotHeader header = 100; //行情公共参数头
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 行情公共参数头结构参见 [QotHeader](./quote.md#6938)

* **返回**

```protobuf
message MarketInfo
{
	required Qot_Common.Security security = 1; //股票代码
	required string name = 2; // 股票名称
	required int32 marketState = 3; //Qot_Common.QotMarketState，市场状态
}

message S2C
{
	repeated MarketInfo marketInfoList = 1; // 市场状态信息
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType，返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 市场状态枚举参见 [QotMarketState](./quote.md#1252)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetMarketState(){
    const { RetType } = Common
    const { SubType, QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功

            const req = {
                c2s: {
                securityList: [
                    {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                ],
                },
            };
            websocket.GetMarketState(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("MarketState: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
MarketState: errCode 0, retMsg , retType 0
{
  "marketInfoList": [{
    "security": {
      "market": 1,
      "code": "00700"
    },
    "name": "腾讯控股",
    "marketState": 3
  }]
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 10 次获取标的市场状态接口。
* 每次请求的股票代码个数上限为 400 个。
:::

---

# 获取资金流向

`GetCapitalFlow(req);`

* **介绍**

    获取资金流向

* **参数**

```protobuf
message C2S
{
	required Qot_Common.Security security = 1; //股票
	optional int32 periodType = 2; // Qot_Common.PeriodType 周期类型
	optional string beginTime = 3; // 开始时间（格式：yyyy-MM-dd），仅周期类型不为实时有效
	optional string endTime = 4; // 结束时间（格式：yyyy-MM-dd），仅周期类型不为实时有效
	optional Qot_Common.QotHeader header = 100; //行情公共参数头
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 周期类型参见 [PeriodType](./quote.md#2644)
>    - 行情公共参数头结构参见 [QotHeader](./quote.md#6938)

* **返回**

```protobuf
message CapitalFlowItem
{
	required double inFlow = 1; // 整体净流入
	optional string time = 2; //开始时间字符串,以分钟为单位
	optional double timestamp = 3; //开始时间戳
	optional double mainInFlow = 4; // 主力大单净流入，仅周期类型不为实时有效
	optional double superInFlow = 5; // 特大单净流入
	optional double bigInFlow = 6; // 大单净流入
	optional double midInFlow = 7; // 中单净流入
	optional double smlInFlow = 8; // 小单净流入
}

message S2C
{
	repeated CapitalFlowItem flowItemList = 1; //资金流向
	optional string lastValidTime = 2; //数据最后有效时间字符串
	optional double lastValidTimestamp = 3; //数据最后有效时间戳
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType,返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetCapitalFlow(){
    const { RetType } = Common
    const { PeriodType, QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功

            const req = {
                c2s: {
                    security: {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                    periodType: PeriodType.PeriodType_INTRADAY,
                },
            };
            websocket.GetCapitalFlow(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("CapitalFlow: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}

```

* **Output**

``` JavaScript
CapitalFlow: errCode 0, retMsg , retType 0
{
  "flowItemList": [{
    "inFlow": -4960940,
    "time": "2022-06-08 09:30:00",
    "timestamp": 1654651800,
    "superInFlow": 0.0,
    "bigInFlow": -4857400.0,
    "midInFlow": -1004904.0,
    "smlInFlow": 9945500.0
  }, ..., {
    "inFlow": 944752820,
    "time": "2022-06-08 10:24:00",
    "timestamp": 1654655040,
    "superInFlow": 53349552.0,
    "bigInFlow": 4287602.0,
    "midInFlow": 24805104.0,
    "smlInFlow": 19382104.0
  }],
  "lastValidTime": "2022-06-08 10:24:00"
}
stop


```

:::tip 接口限制
* 每 30 秒内最多请求 30 次获取资金流向接口。
* 支持正股、窝轮、基金、加密货币。
* 历史周期（日、月、年）仅提供最近 1 年数据；实时周期仅提供最新一天的数据。
* 返回数据只包括盘中数据，不包含盘前盘后数据。
:::

---

# 获取资金分布

`GetCapitalDistribution(req);`

* **介绍**

    获取资金分布

* **参数**

```protobuf
message C2S
{
	required Qot_Common.Security security = 1; //股票
	optional Qot_Common.QotHeader header = 100; //行情公共参数头
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 行情公共参数头结构参见 [QotHeader](./quote.md#6938)

* **返回**

```protobuf
message S2C
{
	optional double capitalInSuper = 9; // 流入资金额度，特大单
	required double capitalInBig = 1; // 流入资金额度，大单
	required double capitalInMid = 2; // 流入资金额度，中单
	required double capitalInSmall = 3; // 流入资金额度，小单
	optional double capitalOutSuper = 10; // 流出资金额度，特大单
	required double capitalOutBig = 4; // 流出资金额度，大单
	required double capitalOutMid = 5; // 流出资金额度，中单
	required double capitalOutSmall = 6; // 流出资金额度，小单
	optional string updateTime = 7; // 更新时间字符串
	optional double updateTimestamp = 8; // 更新时间戳
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType,返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetCapitalDistribution(){
    const { RetType } = Common
    const { SubType, QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功

            const req = {
                c2s: {
                    security: {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                },
            };
            websocket.GetCapitalDistribution(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("CapitalDistribution: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}

```

* **Output**

``` JavaScript
CapitalDistribution: errCode 0, retMsg , retType 0
{
  "capitalInBig": 1586950080,
  "capitalInMid": 2861135060,
  "capitalInSmall": 879906120,
  "capitalOutBig": 890005200,
  "capitalOutMid": 2423820040,
  "capitalOutSmall": 799307540,
  "updateTime": "2021-09-10 11:57:30",
  "updateTimestamp": 1631246250,
  "capitalInSuper": 230158560,
  "capitalOutSuper": 286481380
}
stop

```

:::tip 接口限制
* 每 30 秒内最多请求 30 次获取资金分布接口。
* 支持正股、窝轮、基金、加密货币。
* 更多资金分布介绍，请参考 [这里](https://support.futunn.com/zh-cn/topic498?lang=zh-CN)。
* 返回数据只包括盘中数据，不包含盘前盘后数据。
:::

---

# 获取股票所属板块

`GetOwnerPlate(req);`

* **介绍**

    获取股票的所属板块信息

* **参数**

```protobuf
message C2S
{
	repeated Qot_Common.Security securityList = 1; //股票
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)

* **返回**

```protobuf
message SecurityOwnerPlate
{
	required Qot_Common.Security security = 1; //股票
    optional string name = 3; // 股票名称
	repeated Qot_Common.PlateInfo plateInfoList = 2; //所属板块
}

message S2C
{
	repeated SecurityOwnerPlate ownerPlateList = 1; //所属板块信息
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType，返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 板块信息结构参见 [PlateInfo](./quote.md#2571)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetOwnerPlate(){
    const { RetType } = Common
    const { SubType, QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功

            const req = {
                c2s: {
                    securityList: [
                        {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                        },
                    ],
                },
            };
            websocket.GetOwnerPlate(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("OwnerPlate: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
OwnerPlate: errCode 0, retMsg , retType 0
{
  "ownerPlateList": [{
    "security": {
      "market": 1,
      "code": "00700"
    },
    "plateInfoList": [{
      "plate": {
        "market": 1,
        "code": "HSI Constituent"
      },
      "name": "恒指成份股",
      "plateType": 4
    }, {
      "plate": {
        "market": 1,
        "code": "HSCEI Stock"
      },
      "name": "国指成份股",
      "plateType": 4
    }, ..., {
      "plate": {
        "market": 1,
        "code": "BK1995"
      },
      "name": "区块链",
      "plateType": 3
    }]
  }]
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 10 次获取股票所属板块接口
* 每次请求的股票列表中，股票个数上限为 200 个
* 仅支持正股和指数
:::

---

# 获取历史 K 线

`RequestHistoryKL(req);`

* **介绍**

    获取历史 K 线

* **参数**
```protobuf

message C2S
{
	required int32 rehabType = 1; //Qot_Common.RehabType,复权类型
	required int32 klType = 2; //Qot_Common.KLType,K 线时间周期
	required Qot_Common.Security security = 3; //股票市场以及股票代码
	required string beginTime = 4; //开始时间字符串（格式：yyyy-MM-dd）
	required string endTime = 5; //结束时间字符串（格式：yyyy-MM-dd）
	optional int32 maxAckKLNum = 6; //最多返回多少根 K 线，如果未指定表示不限制
	optional int64 needKLFieldsFlag = 7; //指定返回 K 线结构体特定某几项数据，KLFields 枚举值或组合，如果未指定返回全部字段
	optional bytes nextReqKey = 8; //分页请求 key
	optional bool extendedTime = 9;  //是否获取美股盘前盘后数据，当前仅支持60分钟及以下级别。
    optional int32 session = 10; //是否获取美股盘前盘后以及夜盘数据，当前仅支持60分钟及以下级别，该参数指定后忽略extendedTime
	optional Qot_Common.QotHeader header = 100; //行情公共参数头
}

message Request
{
	required C2S c2s = 1;
}
```
>   - 股票结构参见 [Security](./quote.md#1377)
>   - 复权类型参见 [RehabType](./quote.md#6907)
>   - K 线类型参见 [KLType](./quote.md#4119)
>   - K 线字段类型参见 [KLFields](./quote.md#481)
>   - 行情公共参数头结构参见 [QotHeader](./quote.md#6938)
    
* **返回**

```protobuf

message S2C
{
	required Qot_Common.Security security = 1; //证券
    optional string name = 4; // 股票名称
	repeated Qot_Common.KLine klList = 2; //K 线数据
	optional bytes nextReqKey = 3; //分页请求 key。一次请求没有返回所有数据时，下次请求带上这个 key，会接着请求
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType,返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>   - 股票结构参见 [Security](./quote.md#1377)
>   - K 线结构参见 [KLine](./quote.md#5151)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotRequestHistoryKL(){
    const { RetType } = Common
    const { RehabType, KLType, SubType, QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功

            const req = {
                c2s: {
                    rehabType: RehabType.RehabType_None, 
                    klType: KLType.KLType_Day,
                    security:{
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                    beginTime: "2021-08-05",
                    endTime: "2021-08-10",
                },
            };
            
            websocket.RequestHistoryKL(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("HistoryKL: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
OwnerPlate: errCode 0, retMsg , retType 0
{
  "security": {
    "market": 1,
    "code": "00700"
  },
  "klList": [{
    "time": "2021-08-05 00:00:00",
    "isBlank": false,
    "highPrice": 464.4,
    "openPrice": 452.6,
    "lowPrice": 432.6,
    "closePrice": 439,
    "lastClosePrice": 456.8,
    "volume": "58625939",
    "turnover": 26193545519,
    "turnoverRate": 0.00611,
    "pe": 22.137,
    "changeRate": -3.896672504378286,
    "timestamp": 1628092800
  }, {
    "time": "2021-08-06 00:00:00",
    "isBlank": false,
    "highPrice": 460.4,
    "openPrice": 444.8,
    "lowPrice": 440,
    "closePrice": 453.6,
    "lastClosePrice": 439,
    "volume": "42946505",
    "turnover": 19468783995,
    "turnoverRate": 0.00447,
    "pe": 22.873,
    "changeRate": 3.3257403189066106,
    "timestamp": 1628179200
  }, {
    "time": "2021-08-09 00:00:00",
    "isBlank": false,
    "highPrice": 472.4,
    "openPrice": 447.8,
    "lowPrice": 442.6,
    "closePrice": 461.6,
    "lastClosePrice": 453.6,
    "volume": "40956433",
    "turnover": 18847164570,
    "turnoverRate": 0.00427,
    "pe": 23.276,
    "changeRate": 1.763668430335097,
    "timestamp": 1628438400
  }, {
    "time": "2021-08-10 00:00:00",
    "isBlank": false,
    "highPrice": 493,
    "openPrice": 478,
    "lowPrice": 473.2,
    "closePrice": 486.2,
    "lastClosePrice": 461.6,
    "volume": "40881986",
    "turnover": 19749306230,
    "turnoverRate": 0.00426,
    "pe": 24.517,
    "changeRate": 5.329289428076249,
    "timestamp": 1628524800
  }]
}
stop
```

:::tip 接口限制
* 分 K 提供最近 8 年数据，日 K 提供最近 20 年的数据， 日 K 以上不限制。
* 我们会根据您账户的资产和交易的情况，下发历史 K 线额度。因此，7 天内您只能获取有限只股票的历史 K 线数据。具体规则参见 [订阅额度 & 历史 K 线额度](../intro/authority.md#1314)。您当日消耗的历史 K 线额度，会在 7 天后自动释放。
* 每 30 秒内最多请求 60 次历史 K 线接口。注意：如果您是分页获取数据，此限频规则仅适用于每只股票的首页，后续页请求不受限频规则的限制。
* **换手率**，仅提供日 K 及以上级别。
* **期权**，仅提供日K, 1分K，5分K，15分K，60分K。
* 美股 **盘前、盘后、夜盘 K 线**，仅支持 60 分钟及以下级别。由于美股盘前盘后和夜盘时段为非常规交易时段，此时段的 K 线数据可能不足 2 年。
* 美股的 **成交额**，仅提供 2015-10-12 之后的数据。
:::

---

# 获取复权因子

`RequestRehab(req);`

* **介绍**

    获取股票的复权因子

* **参数**

```protobuf
message C2S
{
	required Qot_Common.Security security = 1; //股票
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)

* **返回**

```protobuf
message S2C
{
	repeated Qot_Common.Rehab rehabList = 1; //复权信息
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType，返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 复权结构参见 [Rehab](./quote.md#7370)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotRequestRehab(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功

            const req = {
                c2s: {
                    security:{
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                },
            };

            websocket.RequestRehab(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("OwnerPlate: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
OwnerPlate: errCode 0, retMsg , retType 0
{
  "rehabList": [{
    "time": "2005-04-19",
    "companyActFlag": "64",
    "fwdFactorA": 1,
    "fwdFactorB": -0.07,
    "bwdFactorA": 1,
    "bwdFactorB": 0.07,
    "dividend": 0.07,
    "timestamp": 1113840000
  }, {
    "time": "2006-05-15",
    "companyActFlag": "64",
    "fwdFactorA": 1,
    "fwdFactorB": -0.08,
    "bwdFactorA": 1,
    "bwdFactorB": 0.08,
    "dividend": 0.08,
    "timestamp": 1147622400
  }, ..., {
    "time": "2021-05-24",
    "companyActFlag": "64",
    "fwdFactorA": 1,
    "fwdFactorB": -1.6,
    "bwdFactorA": 1,
    "bwdFactorB": 1.6,
    "dividend": 1.6,
    "timestamp": 1621785600
  }]
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 60 次获取复权因子接口。
:::

---

# 获取财报日前后价格涨跌幅表现

`GetFinancialsEarningsPriceMove(req);`

* **介绍**

    获取财报日前后价格涨跌幅表现

* **参数**

```protobuf
message C2S
{
    required Qot_Common.Security security = 1; // 股票
    optional int32 periodCount = 2; // 财报周期数量，默认 10，取值范围 [1, 50]
}

message Request
{
    required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)

* **返回**

```protobuf
// 单个交易日的股价行情数据
message PricePerformanceRow
{
    optional int64  tradingDay       = 1; // 交易日时间戳（秒）
    optional string tradingDayStr    = 2; // 交易日字符串，格式 YYYY-MM-DD，对应市场时区
    optional double closePrice       = 3; // 收盘价
    optional double openPrice        = 4; // 开盘价
    optional double highestPrice     = 5; // 最高价
    optional double lowestPrice      = 6; // 最低价
    optional double lastClosePrice   = 7; // 昨收价
    optional double optionIV         = 8; // 期权隐含波动率（百分号前的值，如 12.34 表示 12.34%）
    optional double optionHV         = 9; // 期权历史波动率（百分号前的值，如 12.34 表示 12.34%）
}

// 单期财报周期的行情数据，包含财报元信息及财报日前后若干交易日的价格序列
message ReportCycleQuote
{
    optional int32  fiscalYear        = 1; // 财务年度，如 2024
    optional int32  financialType     = 2; // 财报类型，详见 Qot_Common.F10Type 定义
    optional string periodText        = 3; // 财报周期，如 "2024/Q3"、"2024/FY"
    optional int64  pubTradingDay     = 4; // 财报发布对应的交易日时间戳（秒）
    optional string pubTradingDayStr  = 5; // 财报发布交易日字符串，格式 YYYY-MM-DD，对应市场时区
    optional Qot_Common.EarningsPubTimeType pubType = 6; // 财报发布时间类型，详见 Qot_Common.EarningsPubTimeType 定义
    optional int32  priceInfoIndex    = 7; // itemList 中财报发布当日所在的下标（0-based）；-1 表示无数据
    repeated PricePerformanceRow itemList = 8; // 财报日前后的交易日行情列表，按时间升序排列
}

message S2C
{
    repeated ReportCycleQuote detailList = 1; // 各财报周期的详细行情数据列表，按财报发布日降序排列
}

message Response
{
    required int32  retType = 1 [default = -400]; // 返回结果类型，参见 Common.RetType，0=成功，负数=失败
    optional string retMsg  = 2;                  // 返回结果描述
    optional int32  errCode = 3;                  // 错误码，失败时有效
    optional S2C    s2c     = 4;                  // 响应数据
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)
>    - 财报类型参见 [F10Type](./quote.md#7710)
>    - 财报发布时间类型参见 [EarningsPubTimeType](./quote.md#2586)

* **Example**

```javascript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetFinancialsEarningsPriceMove(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {

            const req = {
                c2s: {
                    security: {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                },
            };
            websocket.GetFinancialsEarningsPriceMove(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("GetFinancialsEarningsPriceMove: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{
        websocket.stop();
        console.log("stop");
    }, 5000);
}
```

* **Output**

``` JavaScript
GetFinancialsEarningsPriceMove: errCode 0, retMsg , retType 0
{
  "detailList": [{
    "fiscalYear": 2026,
    "financialType": 1,
    "periodText": "2026/Q1",
    "pubTradingDay": "1778601600",
    "pubTradingDayStr": "2026-05-13",
    "pubType": "EarningsPubTimeType_Unknown",
    "priceInfoIndex": 5,
    "itemList": [{
      "tradingDay": "1777996800",
      "tradingDayStr": "2026-05-06",
      "closePrice": 463,
      "openPrice": 470.6,
      "highestPrice": 473.4,
      "lowestPrice": 460.2,
      "lastClosePrice": 472.2,
      "optionIV": 31.829,
      "optionHV": 32.22
      //...
    }]
    //...
  }]
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 仅支持港股、美股、新加坡、日本、马来西亚、A股正股。
:::

---

# 获取财报日前后股价历史

`GetFinancialsEarningsPriceHistory(req);`

* **介绍**

    获取财报日前后股价历史

* **参数**

```protobuf
message C2S
{
    required Qot_Common.Security security = 1; // 股票
}

message Request
{
    required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)

* **返回**

```protobuf
// 财报日当日的价格行情数据
message PriceInfo
{
    optional int64  tradingDay       = 1;  // 交易日时间戳（秒）
    optional string tradingDayStr    = 2;  // 交易日字符串，格式 YYYY-MM-DD，对应市场时区
    optional double closePrice       = 3;  // 收盘价
    optional double openPrice        = 4;  // 开盘价
    optional double highestPrice     = 5;  // 最高价
    optional double lowestPrice      = 6;  // 最低价
    optional double lastClosePrice   = 7;  // 昨收价
    optional double volume           = 8;  // 成交量（股）
}

// 相对于财报日的单交易日收盘价
message FinScheduleInfo
{
    optional int32  delta      = 1; // 相对财报发布日的交易日偏移量（负数=发布前，0=发布当日，正数=发布后）
    optional double closePrice = 2; // 该交易日的收盘价
}

// 单期财报周期的历史行情数据，包含财报元信息、预期波动率及财报日当天完整行情
message PriceHistoryOnEarningsDays
{
    optional int32  fiscalYear              = 1;  // 财务年度，如 2024
    optional int32  financialType           = 2;  // 财报类型，详见 Qot_Common.F10Type 定义
    optional string periodText              = 3;  // 财报周期，如 "2024/Q3"、"2024/FY"
    optional bool   isCurrent              = 4;  // 当前时间是否在该财报窗口期
    optional int64  pubTradingDay           = 5;  // 财报发布对应的交易日时间戳（秒）
    optional string pubTradingDayStr        = 6;  // 财报发布交易日字符串，格式 YYYY-MM-DD，对应市场时区
    optional int64  pubTime                 = 7;  // 财报实际发布时间戳（秒，含时分秒）
    optional string pubTimeStr              = 8;  // 财报发布时间字符串，格式 YYYY-MM-DD HH:MM:SS，对应市场时区
    optional Qot_Common.EarningsPubTimeType pubType    = 9;  // 财报发布时间类型，详见 Qot_Common.EarningsPubTimeType 定义
    optional double predictVolaRatioNewest  = 10; // 最新预期波动比例（百分号前的值，如 12.34 表示 12.34%）
    optional double predictVolaRatioHighest = 11; // 最高预期波动比例（百分号前的值，如 12.34 表示 12.34%）
    optional double predictVolaValNewest    = 12; // 最新预期波动金额
    optional double predictVolaValHighest   = 13; // 最高预期波动金额
    optional double optionIVCrush           = 14; // 期权隐含波动率压缩值（百分号前的值，如 12.34 表示 12.34%）
    optional double optionStrikeDateIVCrush = 15; // 行权日期权隐含波动率压缩值（百分号前的值，如 12.34 表示 12.34%）
    optional PriceInfo priceInfo              = 16; // 财报发布日当天的行情数据
    repeated FinScheduleInfo scheduleInfoList = 17; // 相对财报日各交易日收盘价列表，按偏移量升序排列
}

message S2C
{
    repeated PriceHistoryOnEarningsDays detailList = 1; // 各财报周期的详细行情数据列表，按财报发布日降序排列
}

message Response
{
    required int32  retType = 1 [default = -400]; // 返回结果类型，参见 Common.RetType，0=成功，负数=失败
    optional string retMsg  = 2;                  // 返回结果描述
    optional int32  errCode = 3;                  // 错误码，失败时有效
    optional S2C    s2c     = 4;                  // 响应数据
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)
>    - 财报类型参见 [F10Type](./quote.md#7710)
>    - 财报发布时间类型参见 [EarningsPubTimeType](./quote.md#2586)

* **Example**

```javascript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetFinancialsEarningsPriceHistory(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {

            const req = {
                c2s: {
                    security: {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                },
            };
            websocket.GetFinancialsEarningsPriceHistory(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("GetFinancialsEarningsPriceHistory: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{
        websocket.stop();
        console.log("stop");
    }, 5000);
}
```

* **Output**

``` JavaScript
GetFinancialsEarningsPriceHistory: errCode 0, retMsg , retType 0
{
  "detailList": [{
    "fiscalYear": 2026,
    "financialType": 1,
    "periodText": "2026/Q1",
    "isCurrent": true,
    "pubTradingDay": "1778601600",
    "pubTradingDayStr": "2026-05-13",
    "pubTime": "1778601600",
    "pubTimeStr": "2026-05-13 00:00:00",
    "pubType": "EarningsPubTimeType_Unknown",
    "predictVolaRatioNewest": 3.511,
    "predictVolaRatioHighest": 4.225,
    "predictVolaValNewest": 16.603,
    "predictVolaValHighest": 20.037,
    "scheduleInfoList": [{
      "delta": -15,
      "closePrice": 504
      //...
    }]
    //...
  }]
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 仅支持港股、美股、新加坡、日本、马来西亚、A股正股。
:::

---

# 获取财务报表

`GetFinancialsStatements(req);`

* **介绍**

    获取财务报表

* **参数**

```protobuf
message C2S
{
    required Qot_Common.Security security              = 1; // 股票
    optional Qot_Common.FinancialStatementsType statementType = 2; // 财务报表类型，默认利润表（Income=1）
    optional Qot_Common.F10Type      financialType     = 3; // 财报类型，默认 10(QuarterlyAnnual)
    optional string                  currencyCode      = 4; // 币种代码（ISO 4217）
    optional string                  nextKey           = 5; // 分页标识
    optional int32                   num               = 6; // 每页返回数量，默认 10，范围 1~50
}

message Request
{
    required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 财报类型参见 [F10Type](./quote.md#7710)
>    - 财务报表类型参见 [FinancialStatementsType](./quote.md#2910)

* **返回**

```protobuf
// 财报字段结构信息
message FinancialFieldInfo
{
    optional int64  fieldId     = 1; // 财务字段 ID
    optional string displayName = 2; // 字段展示名（当前语言，如"营业收入"）
}

// 单条财务数据项
message FinancialItem
{
    optional int64  fieldId = 1; // 财务字段 ID，与 structureList 中 fieldId 对应
    optional double data    = 2; // 财务数据
    optional double yoy     = 3; // 同比（%）
    optional double qoq     = 4; // 环比（%）
}

// 财务报表
message FinancialReport
{
    optional int64   dateTime            =  1; // 财报截止日时间戳（秒）
    optional string  dateTimeStr         =  2; // 财报截止日时间字符串，格式 YYYY-MM-DD，对应市场时区
    optional int32   fiscalYear          =  3; // 财务年度，如 2024；0 表示无数据
    optional Qot_Common.F10Type financialType =  4; // 财报类型，详见 Qot_Common.F10Type 定义；0 表示未知，下次请求可原样传入
    optional string  periodText          =  5; // 财报周期，如 "2024/Q3"、"2024/FY"
    repeated FinancialItem itemList      =  6; // 财务数据项列表
    optional string  currencyInfo        =  7; // 货币单位（展示型），如 "人民币"、"美元"
    optional string  accountingStandards =  8; // 会计准则，如 "国际会计准则"
    optional string  auditorReport       =  9; // 审计意见，如 "无保留意见"
    optional string  currencyCode        = 10; // 币种代码（ISO 4217），如 "CNY"、"USD"
}

message S2C
{
    repeated FinancialFieldInfo      structureList       = 1; // 字段结构列表，仅收集返回数据中有的字段
    repeated FinancialReport         reportList          = 2; // 财报数据列表，按时间顺序
    optional string                  nextKey             = 3; // 分页标识，"-1" 表示无更多数据
}

message Response
{
    required int32  retType = 1 [default = -400]; // RetType，返回结果
    optional string retMsg  = 2;
    optional int32  errCode = 3;
    optional S2C    s2c     = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)
>    - 财报类型参见 [F10Type](./quote.md#7710)
>    - 财务报表类型参见 [FinancialStatementsType](./quote.md#2910)

* **Example**

```javascript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetFinancialsStatements(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {

            const req = {
                c2s: {
                    security: {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                },
            };
            websocket.GetFinancialsStatements(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("GetFinancialsStatements: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{
        websocket.stop();
        console.log("stop");
    }, 5000);
}
```

* **Output**

``` JavaScript
GetFinancialsStatements: errCode 0, retMsg , retType 0
{
  "structureList": [{
    "fieldId": "5001",
    "displayName": "营业总收入"
    //...
  }],
  "reportList": [{
    "dateTime": "1767110400",
    "dateTimeStr": "2025-12-31",
    "fiscalYear": 2025,
    "financialType": "F10Type_Annual",
    "periodText": "2025/FY",
    "itemList": [{
      "fieldId": "5001",
      "data": 751766000000,
      "yoy": 13.859603154529221
      //...
    }],
    "currencyInfo": "人民币",
    "accountingStandards": "国际会计准则",
    "auditorReport": "无保留意见",
    "currencyCode": "CNY"
    //...
  }],
  "nextKey": "1711814401,2024_1"
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持正股及基金。
:::

---

# 获取主营构成

`GetFinancialsRevenueBreakdown(req);`

* **介绍**

    获取主营构成

* **参数**

```protobuf
message C2S
{
    required Qot_Common.Security security     = 1; // 股票
    optional uint32 date                      = 2; // 筛选时间戳
    optional Qot_Common.F10Type financialType = 3; // 财报类型
    optional string currencyCode              = 4; // 币种代码（ISO 4217）
}

message Request
{
    required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 财报类型参见 [F10Type](./quote.md#7710)
>    - 主营构成维度类型参见 [RevenueBreakdownType](./quote.md#3621)

* **返回**

```protobuf
// 主营构成项
message MainIncomeItem
{
    optional string name           = 1; // 名称
    optional double mainOperIncome = 2; // 营业收入
    optional double ratio          = 3; // 占比，百分号前的值，如 12.34 表示 12.34%
}

// 单一维度主营构成数据
message RevenueBreakdownGroup
{
    optional Qot_Common.RevenueBreakdownType type = 1; // 维度类型（详见 Qot_Common.RevenueBreakdownType 定义）
    repeated MainIncomeItem itemList              = 2; // 该维度主营构成数据列表
}

// 筛选日期
message ScreenDate
{
    optional uint32 date          = 1; // 筛选时间戳（Unix 时间戳（秒），下次请求原样传入）
    optional string periodText    = 2; // 财报周期，如 "2024/Q3"、"2024/FY"
    optional Qot_Common.F10Type financialType = 3; // 财报类型（详见 Qot_Common.F10Type 定义）
}

message S2C
{
    optional string period                        = 1; // 财报周期，如 "2024/Q3"、"2024/FY"
    repeated RevenueBreakdownGroup breakdownList  = 2; // 各维度主营构成数据列表
    optional string currencyCode                  = 3; // 货币代码（ISO 4217）
    repeated ScreenDate screenDateList            = 4; // 可选日期列表，供客户端筛选历史数据，仅 date 与 financialType 都不填时返回
}

message Response
{
    required int32  retType = 1 [default = -400]; // RetType，返回结果
    optional string retMsg  = 2;
    optional int32  errCode = 3;
    optional S2C    s2c     = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)
>    - 财报类型参见 [F10Type](./quote.md#7710)
>    - 主营构成维度类型参见 [RevenueBreakdownType](./quote.md#3621)

* **Example**

```javascript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetFinancialsRevenueBreakdown(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {

            const req = {
                c2s: {
                    security: {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                },
            };
            websocket.GetFinancialsRevenueBreakdown(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("GetFinancialsRevenueBreakdown: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{
        websocket.stop();
        console.log("stop");
    }, 5000);
}
```

* **Output**

``` JavaScript
GetFinancialsRevenueBreakdown: errCode 0, retMsg , retType 0
{
  "period": "2025/FY",
  "breakdownList": [{
    "type": "RevenueBreakdownType_Product",
    "itemList": [{
      "name": "增值服务",
      "mainOperIncome": 369281000000,
      "ratio": 49.1218
      //...
    }]
    //...
  }],
  "currencyCode": "CNY",
  "screenDateList": [{
    "date": 1767110400,
    "periodText": "2025/FY",
    "financialType": "F10Type_Annual"
    //...
  }]
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持正股及基金。
:::

---

# 获取分析师评级概述

`GetResearchAnalystConsensus(req);`

* **介绍**

    获取分析师评级概述

* **参数**

```protobuf
message C2S
{
    required Qot_Common.Security security = 1; // 股票
}

message Request
{
    required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)

* **返回**

```protobuf
message S2C
{
    optional double highest                        = 1;  // 最高目标价
    optional double average                        = 2;  // 平均目标价
    optional double lowest                         = 3;  // 最低目标价
    optional Qot_Common.ResearchRatingType rating  = 4;  // 近3个月分析师综合评级
    optional int32 total                           = 5;  // 近3个月参与评级的分析师总人数
    optional int64 updateTime                      = 6;  // 评级数据更新时间戳（秒）
    optional string updateTimeStr                  = 7;  // 评级数据更新时间字符串，格式 YYYY-MM-DD
    optional double buy                            = 8;  // Buy 评级占比，百分号前的值，如 12.34 表示 12.34%
    optional double hold                           = 9;  // Hold 评级占比，百分号前的值，如 12.34 表示 12.34%
    optional double sell                           = 10; // Sell 评级占比，百分号前的值，如 12.34 表示 12.34%
    optional double strongBuy                      = 11; // Strong Buy 评级占比，百分号前的值，如 12.34 表示 12.34%；仅非美市场
    optional double underperform                   = 12; // Underperform 评级占比，百分号前的值，如 12.34 表示 12.34%；仅非美市场
}

message Response
{
    required int32  retType = 1 [default = -400]; // 返回结果，详见 Common.RetType
    optional string retMsg  = 2;                  // 返回结果描述
    optional int32  errCode = 3;                  // 错误码
    optional S2C    s2c     = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)
>    - 分析师评级，结构参见 [ResearchRatingType](./quote.md#9592)

* **Example**

```javascript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetResearchAnalystConsensus(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {

            const req = {
                c2s: {
                    security: {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                },
            };
            websocket.GetResearchAnalystConsensus(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("GetResearchAnalystConsensus: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{
        websocket.stop();
        console.log("stop");
    }, 5000);
}
```

* **Output**

``` JavaScript
GetResearchAnalystConsensus: errCode 0, retMsg , retType 0
{
  "highest": 820,
  "average": 716,
  "lowest": 579.51,
  "rating": "ResearchRatingType_StrongBuy",
  "total": 44,
  "updateTime": "1778421926",
  "updateTimeStr": "2026-05-10",
  "buy": 22.727,
  "hold": 0,
  "sell": 0,
  "strongBuy": 77.273,
  "underperform": 0
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持正股及 REIT。
:::

---

# 获取评级汇总

`GetResearchRatingSummary(req);`

* **介绍**

    获取评级汇总

* **参数**

```protobuf
message C2S
{
    required Qot_Common.Security security = 1;   // 股票
    optional Qot_Common.ResearchRatingDimensionType ratingDimensionType = 2; // 评级维度（详见 Qot_Common.ResearchRatingDimensionType 定义），默认机构维度
    optional string uid = 3;                     // 空=取该股票的评级汇总列表；非空=取该 uid（institutionUid 或 analystUid）的评级详情
    optional string nextKey = 4;                 // 分页标识，首次不填，续拉时填上次返回的 nextKey；"-1" 表示无更多数据
    optional int32 num = 5;                      // 每页返回数量，默认 10，范围 1~20
}

message Request
{
    required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 评级维度类型参见 [ResearchRatingDimensionType](./quote.md#2247)

* **返回**

```protobuf
message InstInfo
{
    optional string institutionUid         = 1;  // 机构唯一标识
    optional string institutionPictureUrl  = 2;  // 机构图片 URL
    optional string institutionName        = 3;  // 机构名称
    optional int64  updateTime             = 4;  // 更新时间戳（秒）
    optional string updateTimeStr          = 5;  // 更新时间字符串，格式 YYYY-MM-DD，对应市场时区
    optional string institutionSourceName  = 6;  // 机构来源名称
    optional string institutionEnName      = 7;  // 机构英文名称
}

message AnalystInfo
{
    optional string  analystUid        = 1;   // 分析师唯一标识
    optional string  analystName       = 2;   // 分析师姓名
    optional string  analystPictureUrl = 3;   // 分析师头像 URL
    optional double  numOfStars        = 4;   // 星级（0.0~5.0，如 3.50 表示 3.5 星）
    optional double  successRate       = 5;   // 成功率，百分号前的值，如 12.34 表示 12.34%
    optional double  excessReturn      = 6;   // 超额收益，百分号前的值，如 12.34 表示 12.34%
    optional double  stockSuccessRate  = 7;   // 个股成功率，百分号前的值，如 12.34 表示 12.34%
    optional double  stockAvgReturn    = 8;   // 个股平均收益，百分号前的值，如 12.34 表示 12.34%
    optional InstInfo institutionInfo  = 9;   // 所属机构信息
    optional int64   updateTime        = 10;  // 更新时间戳（秒）
    optional string  updateTimeStr     = 11;  // 更新时间字符串，格式 YYYY-MM-DD，对应市场时区
}

message RatingItem
{
    optional string  analystUid            = 1;  // 分析师唯一标识
    optional string  institutionUid        = 2;  // 机构唯一标识
    optional Qot_Common.ResearchRatingType rating = 3; // 评级，仅返回 Sell(1)/Hold(3)/Buy(4)
    optional double  targetPrice           = 4;  // 目标价
    optional int64   recommendationDate    = 5;  // 评级日期时间戳（秒）
    optional string  recommendationDateStr = 6;  // 评级日期字符串，格式 YYYY-MM-DD
    optional string  ratingUrl             = 7;  // 评级来源 URL
    optional int64   updateTime            = 8;  // 更新时间戳（秒）
    optional string  updateTimeStr         = 9;  // 更新时间字符串，格式 YYYY-MM-DD
}

message InstRatingSummaryItem
{
    optional InstInfo  institutionInfo = 1;  // 机构信息
    repeated RatingItem ratingItemList = 2;  // 该机构对该股票的评级记录列表
}

message AnalystRatingSummaryItem
{
    optional AnalystInfo analystInfo    = 1;  // 分析师信息
    repeated RatingItem  ratingItemList = 2;  // 该分析师对该股票的评级记录列表
}

message InstRatingDetail
{
    optional InstInfo    institutionInfo  = 1;  // 机构信息
    repeated AnalystInfo analystInfoList  = 2;  // 机构下的分析师列表
    repeated RatingItem  ratingItemList   = 3;  // 机构下的评级记录列表
}

message AnalystRatingDetail
{
    optional AnalystInfo analystInfo    = 1;  // 分析师信息
    repeated RatingItem  ratingItemList = 2;  // 该分析师对该股票的评级记录列表
}

message S2C
{
    repeated InstRatingSummaryItem    instRatingSummaryList    = 1;  // 机构评级汇总列表
    repeated AnalystRatingSummaryItem analystRatingSummaryList = 2;  // 分析师评级汇总列表
    optional InstRatingDetail         instRatingDetail         = 3;  // 机构评级详情
    optional AnalystRatingDetail      analystRatingDetail      = 4;  // 分析师评级详情
    optional string                   nextKey                  = 5;  // 分页标识，"-1" 表示无更多数据
}

message Response
{
    required int32  retType = 1 [default = -400]; // 返回结果，详见 Common.RetType
    optional string retMsg  = 2;                  // 返回结果描述
    optional int32  errCode = 3;                  // 错误码
    optional S2C    s2c     = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)
>    - 分析师评级参见 [ResearchRatingType](./quote.md#9592)

* **Example**

```javascript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetResearchRatingSummary(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {

            const req = {
                c2s: {
                    security: {
                        market: QotMarket.QotMarket_US_Security,
                        code: "AAPL",
                    },
                },
            };
            websocket.GetResearchRatingSummary(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("GetResearchRatingSummary: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{
        websocket.stop();
        console.log("stop");
    }, 5000);
}
```

* **Output**

``` JavaScript
GetResearchRatingSummary: errCode 0, retMsg , retType 0
{
  "instRatingSummaryList": [{
    "institutionInfo": {
      "institutionUid": "8c9ae25a-07e2-4d52-a511-b0dd115a5224",
      "institutionPictureUrl": "https://foss1.futunn.com/tip_rank_analysts_data_sync/prod/institution/8c9ae25a-07e2-4d52-a511-b0dd115a5224.jpeg",
      "institutionName": "韦德布什",
      "updateTime": "1709278279",
      "updateTimeStr": "2024-03-01",
      "institutionSourceName": "Wedbush",
      "institutionEnName": "Wedbush"
    },
    "ratingItemList": [{
      "institutionUid": "8c9ae25a-07e2-4d52-a511-b0dd115a5224",
      "rating": "ResearchRatingType_Buy",
      "targetPrice": 400,
      "recommendationDate": "1778216400",
      "recommendationDateStr": "2026-05-08",
      "ratingUrl": "https://www.tipranks.com/news/the-fly/apple-price-target-raised-to-400-from-350-at-wedbush-thefly-news",
      "updateTime": "1778322675652242",
      "updateTimeStr": "2026-05-09"
      //...
    }]
    //...
  }],
  "nextKey": "10"
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持美股正股及 REIT。
:::

---

# 获取晨星研究报告

`GetResearchMorningstarReport(req);`

* **介绍**

    获取晨星研究报告

* **参数**

```protobuf
message C2S
{
    required Qot_Common.Security security = 1; // 股票
}

message Request
{
    required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)

* **返回**

```protobuf
// 带更新时间的文本内容
message StringWithUpdateTime {
    optional string context        = 1; // 文本内容
    optional int64  updateTime     = 2; // 更新时间戳（秒）
    optional string updateTimeStr  = 3; // 更新时间字符串，格式 YYYY-MM-DD，对应市场时区
}

message S2C
{
    optional Qot_Common.MorningstarRatingType ratingType              = 1;  // 评级类型（详见 Qot_Common.MorningstarRatingType 定义）
    optional int32                            starRating              = 2;  // 晨星星级评分，取值 1-5 星
    optional int64                            starUpdateTime          = 3;  // 星级更新时间戳（秒）
    optional string                           starUpdateTimeStr       = 4;  // 星级更新时间字符串，格式 YYYY-MM-DD，对应市场时区
    optional double                           fairValue               = 5;  // 公允价值
    optional StringWithUpdateTime             fairValueContent        = 6;  // 公允价值分析文本及更新时间
    optional string                           economicMoatLabel       = 7;  // 护城河评级，如 Wide、Narrow、None
    optional StringWithUpdateTime             economicMoatContent     = 8;  // 护城河分析文本及更新时间
    optional string                           uncertaintyLabel        = 9;  // 不确定性评级，如 Low、Medium、High、Very High、Extreme
    optional StringWithUpdateTime             uncertaintyContent      = 10; // 不确定性分析文本及更新时间
    optional string                           financialHealthLabel    = 11; // 财务健康评级
    optional StringWithUpdateTime             financialHealthContent  = 12; // 财务健康分析文本及更新时间
    repeated string                           analystReportByLine     = 13; // 分析师署名列表，如 ["William Kerwin, CFA"]
    optional int64                            analystReportUpdateTime = 14; // 分析师报告更新时间戳（秒）
    optional string                           analystReportUpdateTimeStr = 15; // 分析师报告更新时间字符串，格式 YYYY-MM-DD，对应市场时区
    repeated StringWithUpdateTime             bullSay                 = 16; // 多方观点列表
    repeated StringWithUpdateTime             bearSay                 = 17; // 空方观点列表
    optional string                           capitalAllocationLabel  = 18; // 资本配置评级
    optional StringWithUpdateTime             capitalAllocationContent = 19; // 资本配置分析文本及更新时间
    optional StringWithUpdateTime             analystNoteTitle        = 20; // 分析师观点标题及更新时间
    optional StringWithUpdateTime             analystNoteContent      = 21; // 分析师观点内容文本及更新时间
    optional StringWithUpdateTime             investmentThesisContent = 22; // 投资论点文本及更新时间
    optional StringWithUpdateTime             fundamentalsContent     = 23; // 基本面报告文本及更新时间
    optional StringWithUpdateTime             valuationContent        = 24; // 估值报告文本及更新时间
    optional string                           pdfUrl                  = 25; // PDF 报告下载链接
}

message Response
{
    required int32  retType = 1 [default = -400]; // 返回结果，详见 Common.RetType
    optional string retMsg  = 2;                  // 返回结果描述
    optional int32  errCode = 3;                  // 错误码
    optional S2C    s2c     = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)
>    - 晨星评级类型参见 [MorningstarRatingType](./quote.md#9433)

* **Example**

```javascript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetResearchMorningstarReport(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {

            const req = {
                c2s: {
                    security: {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                },
            };
            websocket.GetResearchMorningstarReport(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("GetResearchMorningstarReport: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{
        websocket.stop();
        console.log("stop");
    }, 5000);
}
```

* **Output**

``` JavaScript
GetResearchMorningstarReport: errCode 0, retMsg , retType 0
{
  "ratingType": "MorningstarRatingType_Qualitative",
  "starRating": 4,
  "starUpdateTime": "1778257800",
  "starUpdateTimeStr": "2026-05-09",
  "fairValue": 800,
  "fairValueContent": {
    "context": "我们对腾讯控股的每股公平价值估计为800港元。我们的估值中约85%来自于腾讯的核心业务，而剩余的20%来自其投资。我们对核心业务的估值意味着2025年的市盈率为30倍。我们使用加权平均资本成本（WACC）为8.3%来折现公司的自由现金流。我们预计该公司将在五年内实现10%的收入年复合增长率（CAGR）。由于利润率扩大，我们预测腾讯五年内的每股收益（EPS）复合年增长率为14%。\n\n腾讯是一家拥有多重增长驱动因素的企业。我们预计增值服务收入将以8%的五年复合年增长率增长，这主要得益于新游戏的推出以及现有游戏的内容更新。我们预计广告收入将以14%的五年复合年增长...
    "updateTime": "1755138060",
    "updateTimeStr": "2025-08-14"
  },
  "economicMoatLabel": "宽",
  "economicMoatContent": {
    "context": "腾讯的宽护城河主要基于其庞大用户群的网络效应。此外，腾讯还拥有无形资产、成本优势和转换成本等次要护城河来源。鉴于腾讯通过游戏、广告、金融科技和其他渠道已经证明了其利用庞大的用户网络实现货币化的能力，我们认为在未来20年内，腾讯的业务更有可能产生超额投资回报。\n\n腾讯拥有中国领先的通讯应用微信。与其他地区的通讯应用不同，微信是一个日常生活和工作的平台。通过应用内功能，用户可以玩游戏、阅读新闻、进行搜索、观看视频、听音乐以及购物。它本质上是Facebook、WhatsApp、Netflix、Spotify和PayPal的集合体，集成在一个移动应用程序中。这种多功...
    "updateTime": "1766457150",
    "updateTimeStr": "2025-12-23"
  },
  "uncertaintyLabel": "较高",
  "uncertaintyContent": {
    "context": "由于监管风险及其核心业务的竞争强度，我们对腾讯的晨星不确定性评级为高。\n\n在支付领域，2017年出台的强制第三方提供商将客户储备金存入非计息央行账户的规则----以及后来仅给予0.35%利息的让步----表明政策如何实质性地改变了单位经济。\n\n游戏监管同样不可预测：2018年和2021年的许可证审批暂停打乱了发布计划并迫使资源重新分配，而2023年12月发布的旨在遏制视频游戏支出的草案规则（尽管后来被撤回）则突显了该行业的政策负担及长期清晰度的缺乏。\n\n与许多其他上市的中国互联网公司一样，腾讯采用了可变利益实体结构，该结构专门设计用于规避中国在互联网...
    "updateTime": "1766457180",
    "updateTimeStr": "2025-12-23"
  },
  //...
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持正股及 REIT。
:::

---

# 获取个股/指数估值详情

`GetValuationDetail(req);`

* **介绍**

    获取个股/指数估值详情

* **参数**

```protobuf
message C2S
{
    required Qot_Common.Security security = 1;                      // 股票
    optional Qot_Common.ValuationType valuationType = 2;            // 估值类型，详见 Qot_Common.ValuationType 定义，默认 0(Unknown，使用推荐类型)
    optional Qot_Common.ValuationIntervalType intervalType = 3;     // 历史数据时间周期，详见 Qot_Common.ValuationIntervalType 定义
}

message Request
{
    required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 估值类型参见 [ValuationType](./quote.md#5459)
>    - 估值历史区间类型参见 [ValuationIntervalType](./quote.md#971)

* **返回**

```protobuf
// 走势
message ValuationTrend
{
    message ValuationHistoricalItem
    {
        optional double value      = 1; // 估值
        optional uint64 time       = 2; // 时间戳（秒）
        optional string timeStr    = 3; // 时间字符串，格式 YYYY-MM-DD，对应市场时区
        optional double plateValue = 4; // 行业均值
    }
    optional double currentValue         = 1; // 当前估值
    optional double averageValue         = 2; // 历史平均估值
    optional double avgMinus1Stddev      = 3; // 历史平均 - 1σ
    optional double avgPlus1Stddev       = 4; // 历史平均 + 1σ
    optional double valuationPercentile  = 5; // 估值历史分位，百分号前的值，如 12.34 表示 12.34%
    optional double forwardValue         = 6; // 预测估值，仅 PE / PS 有
    repeated ValuationHistoricalItem historicalItems = 7; // 历史数据
}

// 市场分布
message MarketDistribution
{
    message DistributionSection
    {
        optional double start  = 1; // 区间开始值
        optional double end    = 2; // 区间结束值（0 表示无上限）
        optional int32  number = 3; // 该区间个股数量
    }
    repeated DistributionSection sections = 1; // 区间分布（降序）
    optional int32  total        = 2; // 市场总数 / 成分股总数
    optional int32  ranking      = 3; // 该股票估值在市场中的排名（指数无）
    optional double averageValue = 4; // 市场估值均值（指数无）
    optional double medianValue  = 5; // 市场估值中位数（指数无）
}

// 行业分布
message PlateDistribution
{
    message PlateStockItem
    {
        optional Qot_Common.Security security  = 1; // 股票
        optional string              name      = 2; // 个股名称
        optional double              value     = 3; // 估值
        optional double              marketCap = 4; // 市值
    }
    optional Qot_Common.Security plate             = 1; // 所属板块
    optional string              plateName         = 2; // 所属板块名称
    optional double              plateAverageValue = 3; // 板块估值均值
    optional int32               plateRanking      = 4; // 该股票估值在板块中的排名
    optional int32               plateStockItemCount = 5; // 板块个股总数
    repeated PlateStockItem      stockItems        = 6; // 板块成分股估值明细
}

// 盈利 / 营收增速
message ProfitGrowthRate
{
    message ProfitGrowthItem
    {
        optional uint32 financialYear       = 1; // 财报年度
        optional uint32 financialQuarter    = 2; // 财报季度（1=Q1, 2=Q2, 3=Q3, 4=FY）
        optional string periodStr           = 3; // 财报周期，如 "2024/Q3"、"2024/FY"
        optional int64  reportDate          = 4; // 报告日时间戳（秒）
        optional string reportDateStr       = 5; // 报告日字符串，格式 YYYY-MM-DD，对应市场时区
        optional double marketCapMultiple   = 6; // 报告日市值倍数（基准期 = 1）
        optional double financeDataMultiple = 7; // 盈利 / 营收倍数（基准期 = 1，依 valuationType 而定）
    }
    optional double financialTtmMultiple = 1; // TTM 增长倍数
    optional double marketCapMultiple    = 2; // 市值增长倍数
    optional int32  yearCount            = 3; // 计算增长倍数时实际用到的年份数量
    repeated ProfitGrowthItem profitData = 4; // 各期数据
    optional string conclusionDetailed   = 5; // 估值结论描述（已多语言翻译）
}

message S2C
{
    optional Qot_Common.ValuationType valuationType   = 1; // 实际返回的估值类型，详见 Qot_Common.ValuationType 定义
    optional uint64                   lastUpdateTime  = 2; // 最后更新时间戳（秒）
    optional string                   lastUpdateTimeStr = 3; // 最后更新时间字符串，格式 YYYY-MM-DD HH:MM:SS，对应市场时区
    optional ValuationTrend           trend           = 4; // 走势（个股 + 指数）
    optional MarketDistribution       marketDistribution = 5; // 市场分布 / 成分股分布（个股 + 指数）
    optional PlateDistribution        plateDistribution  = 6; // 行业分布（仅个股）
    optional ProfitGrowthRate         profitGrowthRate   = 7; // 盈利 / 营收增速（仅个股，PB 无）
}

message Response
{
    required int32  retType = 1 [default = -400]; // 返回结果，详见 Common.RetType
    optional string retMsg  = 2;                  // 返回结果描述
    optional int32  errCode = 3;                  // 错误码
    optional S2C    s2c     = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)
>    - 估值类型参见 [ValuationType](./quote.md#5459)

* **Example**

```javascript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetValuationDetail(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {

            const req = {
                c2s: {
                    security: {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                },
            };
            websocket.GetValuationDetail(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("GetValuationDetail: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{
        websocket.stop();
        console.log("stop");
    }, 5000);
}
```

* **Output**

``` JavaScript
GetValuationDetail: errCode 0, retMsg , retType 0
{
  "valuationType": "ValuationType_PE",
  "lastUpdateTime": "1778421956",
  "lastUpdateTimeStr": "2026-05-10 22:05:56",
  "trend": {
    "currentValue": 17.266,
    "averageValue": 22.499,
    "avgMinus1Stddev": 20.043,
    "avgPlus1Stddev": 24.955,
    "valuationPercentile": 1.2195121,
    "forwardValue": 15.449,
    "historicalItems": [{
      "value": 22.69,
      "time": "1746979200",
      "timeStr": "2025-05-12",
      "plateValue": 22.678
      //...
    }]
  },
  //...
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持正股、基金及指数。
* PB 估值无盈利/营收增速模块。
* 指数无排名、均值、中位数。
:::

---

# 获取板块/指数成分股估值列表

`GetValuationPlateStockList(req);`

* **介绍**

    获取板块/指数成分股估值列表

* **参数**

```protobuf
message C2S
{
    required Qot_Common.Security security       = 1;  // 股票（板块或指数）
    optional Qot_Common.ValuationType valuationType  = 2;  // 估值类型，详见 Qot_Common.ValuationType 定义，支持 1-3，默认 1(PE)
    optional string nextKey                     = 3;  // 分页标识，首次不填，续拉时填上次返回的 nextKey；"-1" 表示无更多数据
    optional int32 num                          = 4;  // 每页返回数量，默认 10，范围 1~50
    optional Qot_Common.SortType sortType       = 5;  // 排序方向，详见 Qot_Common.SortType 定义，默认升序（SortType_Asc=2）
    optional Qot_Common.SortField sortId        = 6;  // 排序列，详见 Qot_Common.SortField 定义，51=市值（默认）52=估值 53=预测估值 54=历史分位
    optional Qot_Common.Security filterSecurity = 7;  // 仅指数成分股估值有效，按板块筛选成分股，不传则不筛选
}

message Request
{
    required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)

* **返回**

```protobuf
// 指数所属板块条目
message PlateItem
{
    optional Qot_Common.Security security = 1;  // 股票
    optional string name                  = 2;  // 板块名称
}

// 成分股估值条目
message StockItem
{
    optional Qot_Common.Security security = 1;    // 股票
    optional string name                  = 6;    // 股票名称
    optional double valuationVal          = 2;    // 估值
    optional double forwardValue          = 3;    // 预测估值，当前仅支持 PE 和 PS
    optional double valuationPercentile   = 4;    // 估值历史分位，百分号前的值，如 12.34 表示 12.34%
    optional double marketCap             = 5;    // 市值
}

message S2C
{
    optional int32 count                       = 1;  // 成分股总数
    repeated StockItem stockList               = 2;  // 成分股估值列表
    optional string nextKey                    = 3;  // 分页标识，"-1" 表示无更多数据
    repeated PlateItem plateList               = 4;  // 指数成分股所属行业/板块列表；仅在指数全部板块首次请求时返回
}

message Response
{
    required int32  retType = 1 [default = -400]; // 返回结果，详见 Common.RetType
    optional string retMsg  = 2;                  // 返回结果描述
    optional int32  errCode = 3;                  // 错误码
    optional S2C    s2c     = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

```javascript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetValuationPlateStockList(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {

            const req = {
                c2s: {
                    security: {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "LIST23363",
                    },
                },
            };
            websocket.GetValuationPlateStockList(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("GetValuationPlateStockList: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{
        websocket.stop();
        console.log("stop");
    }, 5000);
}
```

* **Output**

``` JavaScript
GetValuationPlateStockList: errCode 0, retMsg , retType 0
{
  "count": 69,
  "stockList": [{
    "security": {
      "market": 1,
      "code": "08076"
    },
    "valuationVal": -2.3,
    "valuationPercentile": 65.3658536,
    "marketCap": 30296520,
    "name": "新利软件"
    //...
  }],
  "nextKey": "10"
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持板块和指数，不支持个股。
* 指数首次全量请求时额外返回所属板块列表（plate_list）。
:::

---

# 获取分红派息

`GetCorporateActionsDividends(req);`

* **介绍**

    获取分红派息

* **参数**

```protobuf
message C2S
{
    required Qot_Common.Security security = 1; // 股票
}

message Request
{
    required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)

* **返回**

```protobuf
// 分红派息单条记录
message DividendItem
{
    optional string pubDate             = 1; // 公告日，格式 YYYY/MM/DD，对应市场时区
    optional string statement           = 2; // 分配方案描述，如"末期息5.3港元"
    optional string process             = 3; // 事件进展，如"方案实施"/"预案"；仅港股和A股的正股与信托有值
    optional string recordDate          = 4; // 股权登记日，格式 YYYY/MM/DD，对应市场时区。ETF无此数据
    optional string exDate              = 5; // 除权除息日，格式 YYYY/MM/DD，对应市场时区
    optional string dividendPayableDate = 6; // 派息日，格式 YYYY/MM/DD，对应市场时区
    optional string fiscalYear          = 7; // 财政年度,如"2026"。仅ETF有值。
}

message S2C
{
    repeated DividendItem dividendList = 1; // 分红派息列表，按公告日倒序排列
}

message Response
{
    required int32  retType = 1 [default = -400]; // 返回结果，详见 Common.RetType
    optional string retMsg  = 2;                  // 返回结果描述
    optional int32  errCode = 3;                  // 错误码
    optional S2C    s2c     = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

```javascript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetCorporateActionsDividends(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {

            const req = {
                c2s: {
                    security: {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                },
            };
            websocket.GetCorporateActionsDividends(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("GetCorporateActionsDividends: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{
        websocket.stop();
        console.log("stop");
    }, 5000);
}
```

* **Output**

``` JavaScript
GetCorporateActionsDividends: errCode 0, retMsg , retType 0
{
  "dividendList": [{
    "pubDate": "2026/03/18",
    "statement": "末期息5.3港元;",
    "process": "预案",
    "recordDate": "2026/05/18",
    "exDate": "2026/05/15",
    "dividendPayableDate": "2026/06/01"
    //...
  }]
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持正股及基金。
:::

---

# 获取回购

`GetCorporateActionsBuybacks(req);`

* **介绍**

    获取回购

* **参数**

```protobuf
message C2S
{
    required Qot_Common.Security security = 1; // 股票
    optional string nextKey = 2; // 分页标识，首次不填，续拉时填上次返回的 nextKey；"-1" 表示无更多数据
    optional int32  num     = 3; // 每页返回数量，默认 10，范围 1~50
}

message Request
{
    required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)

* **返回**

```protobuf
// 港股回购单条记录
message HKBuyBackItem
{
    optional uint64 publDate              = 1;  // 公告日时间戳（秒）
    optional string publDateStr           = 2;  // 公告日字符串，格式 YYYY-MM-DD，对应市场时区
    optional uint64 endDate               = 3;  // 回购截止日时间戳（秒）
    optional string endDateStr            = 4;  // 回购截止日字符串，格式 YYYY-MM-DD，对应市场时区
    optional double buyBackMoney          = 5;  // 回购金额
    optional int64  buyBackSum            = 6;  // 回购股数（股）
    optional double percentage            = 7;  // 占已发行股份百分比，百分号前的值，如 12.34 表示 12.34%
    optional double highPrice             = 8;  // 最高回购价
    optional double lowPrice              = 9;  // 最低回购价
    optional int64  cumulativeSum         = 10; // 本轮累计回购股数（股）
    optional double cumulativePercentage  = 11; // 本轮累计回购占总股本百分比，百分号前的值，如 12.34 表示 12.34%
    optional string shareType             = 12; // 股份类别
}

// A股回购单条记录
message ABuyBackItem
{
    optional uint64 changeRegDate    = 1;  // 工商变更登记日时间戳（秒）
    optional string changeRegDateStr = 2;  // 工商变更登记日字符串，格式 YYYY-MM-DD，对应市场时区
    optional uint64 changeDate       = 3;  // 股份变动日时间戳（秒）
    optional string changeDateStr    = 4;  // 股份变动日字符串，格式 YYYY-MM-DD，对应市场时区
    optional string eventProceDesc   = 5;  // 事件进程描述
    optional uint64 advanceDate      = 6;  // 预案公告日时间戳（秒）
    optional string advanceDateStr   = 7;  // 预案公告日字符串，格式 YYYY-MM-DD，对应市场时区
    optional uint64 meetPassDate     = 8;  // 股东大会通过日时间戳（秒）
    optional string meetPassDateStr  = 9;  // 股东大会通过日字符串，格式 YYYY-MM-DD，对应市场时区
    optional uint64 startDate        = 10; // 回购开始日时间戳（秒）
    optional string startDateStr     = 11; // 回购开始日字符串，格式 YYYY-MM-DD，对应市场时区
    optional uint64 endDate          = 12; // 回购截止日时间戳（秒）
    optional string endDateStr       = 13; // 回购截止日字符串，格式 YYYY-MM-DD，对应市场时区
    optional uint64 payDate          = 14; // 支付日时间戳（秒）
    optional string payDateStr       = 15; // 支付日字符串，格式 YYYY-MM-DD，对应市场时区
    optional string seller           = 16; // 出售方（股份被回购方）
    optional string buyBackMode      = 17; // 回购方式
    optional string shareType        = 18; // 股份类别
    optional int64  buyBackSum       = 19; // 回购股数（股）
    optional double buyBackMoney     = 20; // 回购金额
    optional double percentage       = 21; // 占已发行股份百分比，百分号前的值，如 12.34 表示 12.34%
    optional double valueFloor       = 22; // 拟回购资金总额下限
    optional double valueCeiling     = 23; // 拟回购资金总额上限
    optional double priceFloor       = 24; // 回购价格下限
    optional double priceCeiling     = 25; // 回购价格上限
    optional double volumeFloor      = 26; // 拟回购股数下限
    optional double volumeCeiling    = 27; // 拟回购股数上限
}

message S2C
{
    repeated HKBuyBackItem hkBuyBackList = 1; // 港股回购列表
    repeated ABuyBackItem  aBuyBackList  = 2; // A股回购列表
    optional string nextKey = 3; // 分页标识，"-1" 表示无更多数据
}

message Response
{
    required int32  retType = 1 [default = -400]; // 返回结果，详见 Common.RetType
    optional string retMsg  = 2;                  // 返回结果描述
    optional int32  errCode = 3;                  // 错误码
    optional S2C    s2c     = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

```javascript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetCorporateActionsBuybacks(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {

            const req = {
                c2s: {
                    security: {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                },
            };
            websocket.GetCorporateActionsBuybacks(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("GetCorporateActionsBuybacks: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{
        websocket.stop();
        console.log("stop");
    }, 5000);
}
```

* **Output**

``` JavaScript
GetCorporateActionsBuybacks: errCode 0, retMsg , retType 0
{
  "hkBuyBackList": [{
    "publDate": "1775664000",
    "publDateStr": "2026-04-09",
    "endDate": "1775664000",
    "endDateStr": "2026-04-09",
    "buyBackMoney": 1000880717.6,
    "buyBackSum": "1964000",
    "percentage": 0.021373,
    "highPrice": 514.5,
    "lowPrice": 503,
    "cumulativeSum": "119812000",
    "cumulativePercentage": 1.30386,
    "shareType": "普通股"
    //...
  }],
  "nextKey": "10"
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持港股、A股正股及基金。
:::

---

# 获取拆合股

`GetCorporateActionsStockSplits(req);`

* **介绍**

    获取拆合股

* **参数**

```protobuf
message C2S
{
    required Qot_Common.Security security = 1; // 股票
    optional string nextKey = 2; // 分页标识，首次不填，续拉时填上次返回的 nextKey；"-1" 表示无更多数据
    optional int32  num     = 3; // 每页返回数量，默认 10，范围 1~50
}

message Request
{
    required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)

* **返回**

```protobuf
// 拆合股单条记录
message StockSplitItem
{
    // 通用字段
    optional uint64 dirDeciPubDate        = 1;  // 公告日时间戳（秒）
    optional string dirDeciPubDateStr     = 2;  // 公告日字符串，格式 YYYY-MM-DD，对应市场时区
    optional string reformType            = 3;  // 重组方式
    optional string rate                  = 4;  // 比率

    // 港股专有字段（仅港股的正股与信托有值）
    optional uint64 exDate                = 5;  // 除权日时间戳（秒）
    optional string exDateStr             = 6;  // 除权日字符串，格式 YYYY-MM-DD，对应市场时区
    optional uint64 smDeciDate            = 7;  // 决议日时间戳（秒）
    optional string smDeciDateStr         = 8;  // 决议日字符串，格式 YYYY-MM-DD，对应市场时区
    optional uint64 tempTradeBeginDate    = 9;  // 临时买卖日时间戳（秒）
    optional string tempTradeBeginDateStr = 10; // 临时买卖日字符串，格式 YYYY-MM-DD，对应市场时区
    optional uint64 simulTradeBeginDate   = 11; // 并行买卖开始日时间戳（秒）
    optional string simulTradeBeginDateStr= 12; // 并行买卖开始日字符串，格式 YYYY-MM-DD，对应市场时区
    optional uint64 simulTradeEndDate     = 13; // 并行买卖结束日时间戳（秒）
    optional string simulTradeEndDateStr  = 14; // 并行买卖结束日字符串，格式 YYYY-MM-DD，对应市场时区
    optional string eventStatus           = 15; // 事件进程（如：方案实施）
    optional double newParValue           = 16; // 新面值
    optional string tempShareCode         = 17; // 临时证券代码（如：02988）
    optional string tempShareAbbrName     = 18; // 临时证券简称（如：腾讯控股）
    optional int64  newTradeUnit          = 19; // 新买卖单位（如：100）
    optional double sharesAfterEffect     = 20; // 生效后股数（股）
}

message S2C
{
    repeated StockSplitItem splitItemList = 1; // 拆合股列表
    optional string nextKey = 2; // 分页标识，"-1" 表示无更多数据
}

message Response
{
    required int32  retType = 1 [default = -400]; // 返回结果，详见 Common.RetType
    optional string retMsg  = 2;                  // 返回结果描述
    optional int32  errCode = 3;                  // 错误码
    optional S2C    s2c     = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)
>    - 公司行动重组方式参见 [ReformType](./quote.md#2915)

* **Example**

```javascript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetCorporateActionsStockSplits(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {

            const req = {
                c2s: {
                    security: {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                },
            };
            websocket.GetCorporateActionsStockSplits(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("GetCorporateActionsStockSplits: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{
        websocket.stop();
        console.log("stop");
    }, 5000);
}
```

* **Output**

``` JavaScript
GetCorporateActionsStockSplits: errCode 0, retMsg , retType 0
{
  "splitItemList": [{
    "dirDeciPubDate": "1395158400",
    "dirDeciPubDateStr": "2014-03-19",
    "reformType": "拆股",
    "rate": "1->5",
    "exDate": "1400083200",
    "exDateStr": "2014-05-15",
    "smDeciDate": "1399996800",
    "smDeciDateStr": "2014-05-14",
    "tempTradeBeginDate": "1400083200",
    "tempTradeBeginDateStr": "2014-05-15",
    "simulTradeBeginDate": "1401292800",
    "simulTradeBeginDateStr": "2014-05-29",
    "simulTradeEndDate": "1403107200",
    "simulTradeEndDateStr": "2014-06-19",
    "eventStatus": "方案实施",
    "newParValue": 0.00002,
    "tempShareCode": "02988",
    "tempShareAbbrName": "腾讯控股",
    "newTradeUnit": "100",
    "sharesAfterEffect": 9319999970
  }],
  "nextKey": "-1"
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持港股、美股、日本、新加坡、马来西亚正股及基金。
:::

---

# 获取持股统计

`GetShareholdersOverview(req);`

* **介绍**

    获取持股统计

* **参数**

```protobuf
message C2S
{
    required Qot_Common.Security security = 1; // 股票
    optional int32               periodId = 3; // 指定报告期 ID；传 0 或不传则返回最新数据，并额外返回可用报告期列表
}

message Request
{
    required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)

* **返回**

```protobuf
message OwnershipStaticItem
{
    optional string name      = 1; // 持股人/分组名称
    optional double holderPct = 2; // 持股占比（百分比），如 23.37 表示 23.37%
    optional int32  holderId  = 3; // 股东 ID；mainHolderInfoList 中有值，其他分组为 0
}

message OwnershipStaticInfo
{
    optional uint64 staticDate    = 1; // 统计日期时间戳（秒）
    optional string staticDateStr = 2; // 统计日期字符串，格式 YYYY-MM-DD，对应市场时区
    repeated OwnershipStaticItem itemList = 4; // 持股统计子项列表
}

// 报告期条目
message HoldingPeriodItem
{
    optional string periodText = 1; // 报告期，如 "2025/Q3"
    optional int32  periodId   = 2; // 报告期 ID，下次请求原样传入
}

message S2C
{
    repeated OwnershipStaticInfo mainHolderInfoList = 1; // 主要股东列表
    repeated OwnershipStaticInfo holderTypeInfoList = 2; // 持股类型列表
    repeated HoldingPeriodItem   holdingPeriodList  = 3; // 可用报告期列表，仅当请求 periodId 为 0 时返回
}

message Response
{
    required int32  retType = 1 [default = -400]; // 返回结果，详见 Common.RetType
    optional string retMsg  = 2;                  // 返回结果描述
    optional int32  errCode = 3;                  // 错误码
    optional S2C    s2c     = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

```javascript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetShareholdersOverview(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {

            const req = {
                c2s: {
                    security: {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                },
            };
            websocket.GetShareholdersOverview(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("GetShareholdersOverview: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{
        websocket.stop();
        console.log("stop");
    }, 5000);
}
```

* **Output**

``` JavaScript
GetShareholdersOverview: errCode 0, retMsg , retType 0
{
  "mainHolderInfoList": [{
    "staticDate": "1778422007",
    "staticDateStr": "2026-05-10",
    "itemList": [{
      "name": "Prosus Ventures N.V.",
      "holderPct": 23.05351,
      "holderId": 337488017
      //...
    }]
  }],
  "holderTypeInfoList": [{
    "staticDate": "1778422007",
    "staticDateStr": "2026-05-10",
    "itemList": [{
      "name": "风险资本/私募股权投资",
      "holderPct": 23.14464
      //...
    }]
  }],
  "holdingPeriodList": [{
    "periodText": "2026/Q1",
    "periodId": 89
    //...
  }]
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持港股、美股、新加坡、日本、马来西亚正股及基金。
:::

---

# 获取持股变动

`GetShareholdersHoldingChanges(req);`

* **介绍**

    获取持股变动

* **参数**

```protobuf
message C2S
{
    required Qot_Common.Security security = 1;  // 股票
    optional string nextKey   = 2;  // 分页标识，首次不填，续拉时填上次返回的 nextKey；"-1" 表示无更多数据
    optional int32  num       = 3;  // 每页返回数量，默认 10，范围 1~50
    optional Qot_Common.SortType sortType   = 4;  // 排序方向，详见 Qot_Common.SortType 定义，默认降序
    optional Qot_Common.SortField sortColumn = 5; // 排序字段，详见 Qot_Common.SortField，62=持股变动数（默认）63=持股日期 64=变动比例 65=变动金额 66=持股比例
    optional Qot_Common.HoldingChangesFilterType filterType = 6; // 筛选类型，详见 Qot_Common.HoldingChangesFilterType 定义，默认全部
}

message Request
{
    required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 排序方式参见 [SortType](./quote.md#7169)
>    - 排序字段参见 [SortField](./quote.md#2930)
>    - 持股变动筛选类型参见 [HoldingChangesFilterType](./quote.md#2442)

* **返回**

```protobuf
message OwnerListItem
{
    optional string periodText         = 1;  // 报告期，如 "2025/Q3"
    optional string name               = 2;  // 股东名称
    optional int32  holderId           = 3;  // 股东 ID，用于请求历史变动明细
    optional int64  shareChangeNum     = 4;  // 持股变动数（单位：股）
    optional int64  sharesChangePrice  = 5;  // 参考变动金额
    optional double holderPct          = 6;  // 持股比例，百分号前的值，如 12.34 表示 12.34%
    optional string holderType         = 7;  // 持股性质（文本，如"传统投资经理"）
    optional int32  holderTypeId       = 8;  // 持股性质 ID，用于请求历史变动明细
    optional uint64 holdingDate        = 9;  // 报告日期时间戳（秒）
    optional string holdingDateStr     = 10; // 报告日期字符串，格式 YYYY-MM-DD，香港时区
    optional double holderPctChange    = 11; // 持股变动比例，百分号前的值，如 12.34 表示变动 12.34%
    optional int64  holderQuantity     = 12; // 持股数（单位：股）
}

message S2C
{
    repeated OwnerListItem itemList = 1;  // 持股变动记录列表
    optional string nextKey         = 2;  // 分页标识，"-1" 表示无更多数据
}

message Response
{
    required int32  retType = 1 [default = -400]; // 返回结果，详见 Common.RetType
    optional string retMsg  = 2;                  // 返回结果描述
    optional int32  errCode = 3;                  // 错误码
    optional S2C    s2c     = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

```javascript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetShareholdersHoldingChanges(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {

            const req = {
                c2s: {
                    security: {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                },
            };
            websocket.GetShareholdersHoldingChanges(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("GetShareholdersHoldingChanges: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{
        websocket.stop();
        console.log("stop");
    }, 5000);
}
```

* **Output**

``` JavaScript
GetShareholdersHoldingChanges: errCode 0, retMsg , retType 0
{
  "itemList": [{
    "periodText": "2026/Q1",
    "name": "贝莱德",
    "holderId": 403413,
    "shareChangeNum": "8012783",
    "sharesChangePrice": "3777225906",
    "holderPct": 2.67,
    "holderType": "传统投资经理",
    "holderTypeId": 2,
    "holdingDate": "1774886400",
    "holdingDateStr": "2026-03-31",
    "holderPctChange": 0.088,
    "holderQuantity": "240875698"
    //...
  }],
  "nextKey": "10"
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持港股、美股、新加坡、马来西亚、日本正股及基金。
:::

---

﻿# 获取持股明细

`GetShareholdersHolderDetail(req);`

* **介绍**

    获取持股明细

* **参数**

```protobuf
message C2S
{
    required Qot_Common.Security security = 1;
    optional Qot_Common.HolderDetailType requestType = 2; // 请求数据类型，详见 Qot_Common.HolderDetailType 定义，默认按服务端默认逻辑返回
    optional string nextKey = 3;              // 分页标识，首次不填，续拉时填上次返回的 nextKey；"-1" 表示无更多数据
    optional int32 num = 4;                   // 每页返回数量，默认 10，范围 1~50
    optional Qot_Common.SortField sortColumn = 5; // 排序列，详见 Qot_Common.SortField，61=持股股数（默认）62=持股变动数
    optional Qot_Common.SortType sortType   = 6;  // 排序方向，详见 Qot_Common.SortType 定义，默认降序
    optional int32 periodId = 7;              // 指定统计周期 ID；与 Qot_GetShareholdersOverview（3237）返回的 holdingPeriodList 中 periodId 一致；默认 0 表示最新周期
    optional int32 holderId = 8;              // 按持股人 ID 过滤；默认 0 表示不过滤；可取自 GetShareholdersOverview（3237）、GetShareholdersHoldingChanges（3238）、本协议（3239）、GetInsiderHolderList（3241）、GetInsiderTradeList（3242）返回的 holderId
}

message Request
{
    required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 持股类型参见 [HolderDetailType](./quote.md#8148)
>    - 排序字段参见 [SortField](./quote.md#2930)
>    - 排序方向参见 [SortType](./quote.md#7169)

* **返回**

```protobuf
message OwnershipDetailItem
{
    optional string periodText = 1;           // 报告期，如 "2025/Q3"
    optional uint64 holderId = 2;             // 持股人 ID
    optional string name = 3;                 // 股东名称
    optional int64 holderQuantity = 4;        // 总持股数（股）
    optional int64 holderQuantityChange = 5;  // 持股变动数（股，正为增持，负为减持）
    optional double holderPct = 6;            // 持股比例（%），如 12.34 表示 12.34%
    optional double holderPctChange = 7;      // 持股变动比例（%），如 12.34 表示 12.34%；负值为减少
    optional uint64 holdingDate = 8;          // 持股日期时间戳（秒）
    optional string holdingDateStr = 9;       // 持股日期字符串，格式 YYYY-MM-DD，香港时区
    optional double closePrice = 10;          // 持股日期对应收盘价（真实价格）
    optional double priceChangePct = 11;      // 持股日期对应涨跌幅（%），如 -0.4467 表示 -0.4467%
    optional string sourceGroupName = 12;     // 持股明细披露信息来源（如 13F、多份文件等）
}

message S2C
{
    optional uint64 updateTime = 1;           // 数据更新时间戳（秒）
    optional string updateTimeStr = 2;        // 数据更新时间字符串，格式 YYYY-MM-DD HH:MM:SS，对应市场时区
    optional string nextKey = 3;              // 分页标识，"-1" 表示无更多数据
    repeated OwnershipDetailItem itemList = 4;
}

message Response
{
    required int32  retType = 1 [default = -400]; // 返回结果，详见 Common.RetType
    optional string retMsg  = 2;                  // 返回结果描述
    optional int32  errCode = 3;                  // 错误码
    optional S2C    s2c     = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)
>    - 股东持仓明细机构类型参见 [HolderDetailType](./quote.md#8148)

* **Example**

```javascript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetShareholdersHolderDetail(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {

            const req = {
                c2s: {
                    security: {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                },
            };
            websocket.GetShareholdersHolderDetail(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("GetShareholdersHolderDetail: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{
        websocket.stop();
        console.log("stop");
    }, 5000);
}
```

* **Output**

``` JavaScript
GetShareholdersHolderDetail: errCode 0, retMsg , retType 0
{
  "updateTime": "1778344379",
  "updateTimeStr": "2026-05-10 00:32:59",
  "nextKey": "10",
  "itemList": [{
    "periodText": "2026/Q1",
    "holderId": "337488017",
    "name": "Prosus Ventures N.V.",
    "holderQuantity": "2079512000",
    "holderQuantityChange": "-25741100",
    "holderPct": 23.053,
    "holderPctChange": -0.285,
    "holdingDate": "1767110400",
    "holdingDateStr": "2025-12-31",
    "closePrice": 599,
    "priceChangePct": -0.1666,
    "sourceGroupName": "年报"
    //...
  }]
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持港股、美股、新加坡、日本、马来西亚正股及基金。
* 支持分页，默认每页 10 条；分页标识为字符串类型。
:::

---

# 获取机构持股

`GetShareholdersInstitutional(req);`

* **介绍**

    获取机构持股

* **参数**

```protobuf
message C2S
{
    required Qot_Common.Security security = 1;
    optional string nextKey = 2;    // 分页标识，首次不填，续拉时填上次返回的 nextKey；"-1" 表示无更多数据
    optional int32  num     = 3;    // 每页返回数量，默认 10，范围 1~50
}

message Request
{
    required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)

* **返回**

```protobuf
message InstitutionHolderItem
{
    optional string periodText = 1;               // 报告期，如 "2025/Q3"
    optional int64 institutionQuantity = 2;       // 机构持股机构数量（家）
    optional int64 institutionQuantityChange = 3; // 机构持股机构数量变化
    optional int64 holderQuantity = 4;            // 机构持股总股数（股）
    optional int64 holderQuantityChange = 5;      // 机构持股总股数变化
    optional double holderPct = 6;                // 持股比例（%），如 12.34 表示 12.34%
    optional double holderPctChange = 7;          // 持股比例变动（%），如 12.34 表示变动 12.34%
}

message S2C
{
    optional uint64 updateTime = 1;            // 数据更新时间戳（秒）
    optional string updateTimeStr = 2;         // 数据更新时间字符串，格式 YYYY-MM-DD HH:MM:SS，对应市场时区
    optional string nextKey = 3;               // 分页标识，"-1" 表示无更多数据
    repeated InstitutionHolderItem itemList = 4;
}

message Response
{
    required int32  retType = 1 [default = -400]; // 返回结果，详见 Common.RetType
    optional string retMsg  = 2;                  // 返回结果描述
    optional int32  errCode = 3;                  // 错误码
    optional S2C    s2c     = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

```javascript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetShareholdersInstitutional(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {

            const req = {
                c2s: {
                    security: {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                },
            };
            websocket.GetShareholdersInstitutional(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("GetShareholdersInstitutional: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{
        websocket.stop();
        console.log("stop");
    }, 5000);
}
```

* **Output**

``` JavaScript
GetShareholdersInstitutional: errCode 0, retMsg , retType 0
{
  "updateTime": "1778423150",
  "updateTimeStr": "2026-05-10 22:25:50",
  "nextKey": "1696089599",
  "itemList": [{
    "periodText": "2026/Q1",
    "institutionQuantity": "864",
    "institutionQuantityChange": "-9",
    "holderQuantity": "4190299486",
    "holderQuantityChange": "-3883834",
    "holderPct": 46.453,
    "holderPctChange": 0.021
    //...
  }]
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持港股、美股、新加坡、日本、马来西亚正股及基金。
* 支持分页，默认每页 10 条；分页标识为字符串类型。
:::

---

# 获取内部人持股列表

`GetInsiderHolderList(req);`

* **介绍**

    获取内部人持股列表

* **参数**

```protobuf
message C2S
{
    required Qot_Common.Security security = 1;
    optional string nextKey = 2; // 分页标识，首次不填，续拉时填上次返回的 nextKey；"-1" 表示无更多数据
    optional int32  num     = 3; // 每页返回数量，默认 10，范围 1~20
}

message Request
{
    required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)

* **返回**

```protobuf
message OwnerInsiderHolderItem
{
    optional int64  holderId       = 1; // 股东id，可作为 GetInsiderTradeList 和 Qot_GetShareholdersHolderDetail 的入参
    optional int64  holderQuantity = 2; // 总持股数
    optional double holderPct      = 3; // 持股比例，百分号前的值，如 12.34 表示 12.34%
    optional string name           = 4; // 股东名称
    optional string title          = 5; // 股东职位
}

message S2C
{
    repeated OwnerInsiderHolderItem itemList           = 1;
    optional int32                  allCount           = 2;  // 总数
    optional string                 nextKey            = 3;  // 分页标识，"-1" 表示无更多数据
    optional int32                  insiderTotalCount  = 4;  // 内部人总人数，仅首次请求（nextKey为空）时返回
    optional int32                  insiderBoughtCount = 5;  // 内部人买入总人数，仅首次请求时返回
    optional int32                  insiderSoldCount   = 6;  // 内部人卖出总人数，仅首次请求时返回
}

message Response
{
    required int32  retType = 1 [default = -400]; // 返回结果，详见 Common.RetType
    optional string retMsg  = 2;                  // 返回结果描述
    optional int32  errCode = 3;                  // 错误码
    optional S2C    s2c     = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

```javascript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetInsiderHolderList(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {

            const req = {
                c2s: {
                    security: {
                        market: QotMarket.QotMarket_US_Security,
                        code: "AAPL",
                    },
                },
            };
            websocket.GetInsiderHolderList(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("GetInsiderHolderList: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{
        websocket.stop();
        console.log("stop");
    }, 5000);
}
```

* **Output**

``` JavaScript
GetInsiderHolderList: errCode 0, retMsg , retType 0
{
  "itemList": [{
    "holderId": "234085",
    "holderQuantity": "4125576",
    "holderPct": 0.028,
    "name": "Arthur Levinson",
    "title": "独立非执行主席"
    //...
  }],
  "allCount": 17,
  "nextKey": "10",
  "insiderTotalCount": 17,
  "insiderBoughtCount": 11,
  "insiderSoldCount": 8
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 仅美股、新加坡正股及基金有意义。
* 支持分页，默认每页 10 条，最多 20 条；分页标识为字符串类型。
* 仅首页（首次请求，nextKey 为空）额外返回内部人统计摘要（总人数/买入人数/卖出人数）。
:::

---

# 获取内部人交易

`GetInsiderTradeList(req);`

* **介绍**

    获取内部人交易列表

* **参数**

```protobuf
message C2S
{
    required Qot_Common.Security security    = 1;
    optional int64 holderId                  = 2; // 股东id，非必传，传了为指定某一个股东；可取自 GetInsiderHolderList（3241）或本协议（3242）返回的 holderId
    optional string nextKey                  = 3; // 分页标识，首次不填，续拉时填上次返回的 nextKey；"-1" 表示无更多数据
    optional int32  num                      = 4; // 每页返回数量，默认 10，范围 1~50
}

message Request
{
    required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)

* **返回**

```protobuf
message OwnerInsiderTradeItem
{
    optional int64  tradeShares                = 1;  // 交易股数
    optional int64  minTradeDate               = 2;  // 最小交易日期时间戳（秒）
    optional string minTradeDateStr            = 3;  // 最小交易日期字符串，格式 YYYY-MM-DD，对应市场时区
    optional int64  maxTradeDate               = 4;  // 最大交易日期时间戳（秒）
    optional string maxTradeDateStr            = 5;  // 最大交易日期字符串，格式 YYYY-MM-DD，对应市场时区
    optional double minPrice                   = 6;  // 最小交易价格
    optional double maxPrice                   = 7;  // 最大交易价格
    optional int64  securityHolderQuantity     = 8;  // 证券类型持股数
    optional bool   isProposedSaleOfSecurities = 9;  // 是否为计划出售证券
    optional int64  holderId                   = 10; // 股东id
    optional string name                       = 11; // 股东名称
    optional string title                      = 12; // 股东职位
    optional string securityDescription        = 13; // 证券类型描述
    optional string transactionType            = 14; // 交易类型
    optional string sourceGroupName            = 15; // 交易数据来源
}

message S2C
{
    repeated OwnerInsiderTradeItem itemList = 1;
    optional int32 allCount                 = 2; // 总数
    optional string nextKey                 = 3; // 分页标识，"-1" 表示无更多数据
}

message Response
{
    required int32  retType = 1 [default = -400]; // 返回结果，详见 Common.RetType
    optional string retMsg  = 2;                  // 返回结果描述
    optional int32  errCode = 3;                  // 错误码
    optional S2C    s2c     = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

```javascript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetInsiderTradeList(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {

            const req = {
                c2s: {
                    security: {
                        market: QotMarket.QotMarket_US_Security,
                        code: "AAPL",
                    },
                },
            };
            websocket.GetInsiderTradeList(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("GetInsiderTradeList: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{
        websocket.stop();
        console.log("stop");
    }, 5000);
}
```

* **Output**

``` JavaScript
GetInsiderTradeList: errCode 0, retMsg , retType 0
{
  "itemList": [{
    "tradeShares": "-250000",
    "minTradeDate": "1777996800",
    "minTradeDateStr": "2026-05-05",
    "maxTradeDate": "1777996800",
    "maxTradeDateStr": "2026-05-05",
    "minPrice": 284.760656,
    "maxPrice": 284.760656,
    "isProposedSaleOfSecurities": true,
    "holderId": "234085",
    "name": "Arthur Levinson",
    "title": "独立非执行主席",
    "securityDescription": "普通股",
    "transactionType": "意向出售",
    "sourceGroupName": "Form 144"
    //...
  }],
  "allCount": 188,
  "nextKey": "10"
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 仅美股、新加坡正股及基金有意义。
* 支持分页，默认每页 10 条，最多 50 条；分页标识为字符串类型。
* holderId 可取自 GetInsiderHolderList（3241）或本协议（3242）的返回值。
:::

---

# 获取公司概况

`GetCompanyProfile(req);`

* **介绍**

    获取公司概况

* **参数**

```protobuf
message C2S
{
    required Qot_Common.Security security = 1; // 股票
}

message Request
{
    required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)

* **返回**

```protobuf
// 公司详情标签项
message CompanyLabItem
{
    optional string    name      = 1; // 标签名
    optional string    value     = 2; // 标签对应信息
    optional Qot_Common.CompanyProfileFieldType fieldType = 3; // 标签类型
}

message S2C
{
    repeated CompanyLabItem itemList = 1; // 公司详情标签列表
}

message Response
{
    required int32  retType = 1 [default = -400]; // 返回结果，详见 Common.RetType
    optional string retMsg  = 2;                  // 返回结果描述
    optional int32  errCode = 3;                  // 错误码
    optional S2C    s2c     = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)
>    - 公司资料字段类型参见 [CompanyProfileFieldType](./quote.md#2227)

* **Example**

```javascript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetCompanyProfile(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {

            const req = {
                c2s: {
                    security: {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                },
            };
            websocket.GetCompanyProfile(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("GetCompanyProfile: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{
        websocket.stop();
        console.log("stop");
    }, 5000);
}
```

* **Output**

``` JavaScript
GetCompanyProfile: errCode 0, retMsg , retType 0
{
  "itemList": [{
    "name": "公司代码",
    "value": "00700",
    "fieldType": "CompanyProfileFieldType_SourceText"
    //...
  }]
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持正股及基金。
:::

---

# 获取高管信息

`GetCompanyExecutives(req);`

* **介绍**

    获取高管信息

* **参数**

```protobuf
message C2S
{
    required Qot_Common.Security security = 1; // 股票
}

message Request
{
    required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)

* **返回**

```protobuf
// 公司高管信息项
message DirectorInfo
{
    optional string displayLeaderName   = 1;  // 高管展示名称（仅用于展示，不用于查询背景接口）
    optional string leaderName          = 2;  // 高管姓名（可传入 GetCompanyExecutiveBackground 查询背景）
    optional string positionName        = 3;  // 职位名称
    optional uint64 beginDate           = 4;  // 任职起始日时间戳（秒）
    optional string beginDateStr        = 5;  // 任职起始日字符串，格式 YYYY-MM-DD，对应市场时区
    optional string leaderGender        = 6;  // 性别，如 "Male" / "Female"
    optional string leaderAge           = 7;  // 年龄，字符串形式，如 "62"
    optional string highestEducation    = 8;  // 最高学历
    optional uint64 annualSalary        = 9;  // 年薪
    optional uint64 issueDate           = 10; // 发布日期时间戳（秒）
    optional string issueDateStr        = 11; // 发布日期字符串，格式 YYYY-MM-DD，对应市场时区
}

message S2C
{
    repeated DirectorInfo directorList = 1; // 董事高管列表
}

message Response
{
    required int32  retType = 1 [default = -400]; // 返回结果，详见 Common.RetType
    optional string retMsg  = 2;                  // 返回结果描述
    optional int32  errCode = 3;                  // 错误码
    optional S2C    s2c     = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

```javascript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetCompanyExecutives(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {

            const req = {
                c2s: {
                    security: {
                        market: QotMarket.QotMarket_US_Security,
                        code: "AAPL",
                    },
                },
            };
            websocket.GetCompanyExecutives(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("GetCompanyExecutives: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{
        websocket.stop();
        console.log("stop");
    }, 5000);
}
```

* **Output**

``` JavaScript
GetCompanyExecutives: errCode 0, retMsg , retType 0
{
  "directorList": [{
    "displayLeaderName": "Timothy D. Cook",
    "leaderName": "Mr. Timothy D. Cook",
    "positionName": "Director and Chief Executive Officer",
    "leaderGender": "男",
    "leaderAge": "65",
    "annualSalary": 74294811,
    "issueDate": 1776614400,
    "issueDateStr": "2026-04-19"
    //...
  }]
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持正股及基金。
:::

---

# 获取高管背景

`GetCompanyExecutiveBackground(req);`

* **介绍**

    获取高管背景

* **参数**

```protobuf
message C2S
{
    required Qot_Common.Security security = 1; // 股票
    optional string leaderName            = 2; // 高管姓名（使用 GetCompanyExecutives 返回的 leaderName 字段）
}

message Request
{
    required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)

* **返回**

```protobuf
message S2C
{
    optional string briefBackground = 1; // 高管背景简介
}

message Response
{
    required int32  retType = 1 [default = -400]; // 返回结果，详见 Common.RetType
    optional string retMsg  = 2;                  // 返回结果描述
    optional int32  errCode = 3;                  // 错误码
    optional S2C    s2c     = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

```javascript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetCompanyExecutiveBackground(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {

            const req = {
                c2s: {
                    security: {
                        market: QotMarket.QotMarket_US_Security,
                        code: "AAPL",
                    },
                    leaderName: "Mr. Timothy D. Cook",
                },
            };
            websocket.GetCompanyExecutiveBackground(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("GetCompanyExecutiveBackground: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{
        websocket.stop();
        console.log("stop");
    }, 5000);
}
```

* **Output**

``` JavaScript
GetCompanyExecutiveBackground: errCode 0, retMsg , retType 0
{
  "briefBackground": "2026年4月20日，苹果公司宣布，蒂姆·库克将从首席执行官职位转任苹果董事会执行主席，自2026年9月1日起生效。现年65岁的库克自2011年起担任苹果首席执行官，此前曾于2005年10月至2011年担任苹果首席运营官。库克于1998年3月加入苹果，并于2002年2月至2005年10月担任全球销售与运营执行副总裁。2000年10月至2002年2月，库克担任全球运营、销售、服务与支持高级副总裁。1998年3月至2000年10月，库克担任全球运营高级副总裁。此外，库克还担任美国国家橄榄球基金会暨大学名人堂公司董事会成员、杜克大学校董会成员，以及马拉拉基...
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持正股及基金。
:::

---

# 获取经营效率

`GetCompanyOperationalEfficiency(req);`

* **介绍**

    获取经营效率

* **参数**

```protobuf
message C2S
{
    required Qot_Common.Security security      = 1; // 股票
    optional string nextKey                    = 2; // 分页标识，首次不填，续拉时填上次返回的 nextKey；"-1" 表示无更多数据
    optional int32  num                        = 3; // 每页返回数量，默认 10，范围 1~50
    optional string currencyCode               = 4; // 货币代码(ISO 4217)，如 CNY、USD、HKD、SGD、JPY、CAD、AUD；不传返回默认货币
    optional Qot_Common.F10Type financialType  = 5; // 财报周期筛选，支持 0-7，默认 0(不限)
}

message Request
{
    required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 财报类型参见 [F10Type](./quote.md#7710)

* **返回**

```protobuf
message S2C
{
    repeated OperationalEfficiencyItem itemList = 1; // 经营效率数据列表
    optional string nextKey                     = 2; // 分页标识，"-1" 表示无更多数据
    optional string currencyCode                = 3; // 货币代码(ISO 4217)
}

message Response
{
    required int32  retType = 1 [default = -400]; // 返回结果，详见 Common.RetType
    optional string retMsg  = 2;                  // 返回结果描述
    optional int32  errCode = 3;                  // 错误码
    optional S2C    s2c     = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)
>    - 财报类型参见 [F10Type](./quote.md#7710)

* **Example**

```javascript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetCompanyOperationalEfficiency(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {

            const req = {
                c2s: {
                    security: {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                },
            };
            websocket.GetCompanyOperationalEfficiency(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("GetCompanyOperationalEfficiency: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{
        websocket.stop();
        console.log("stop");
    }, 5000);
}
```

* **Output**

``` JavaScript
GetCompanyOperationalEfficiency: errCode 0, retMsg , retType 0
{
  "itemList": [{
    "fiscalYear": 2025,
    "financialType": "F10Type_Annual",
    "periodText": "2025/FY",
    "endDate": "1767110400",
    "endDateStr": "2025-12-31",
    "employeeNum": "115849",
    "employeeNumYoy": 4.7857,
    "incomePerCapita": 6489188.5126,
    "incomePerCapitaYoy": 8.6594,
    "profitPerCapita": 2085145.3184,
    "profitPerCapitaYoy": 10.7787,
    "netProfitPerCapita": 1983625.2362,
    "netProfitPerCapitaYoy": 11.6246
    //...
  }],
  "nextKey": "1483113600",
  "currencyCode": "CNY"
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持正股及基金。
:::

---

# 获取十大经纪商买卖数据

`GetTopTenBuySellBrokers(req);`

* **介绍**

    获取十大经纪商买卖数据

* **参数**

```protobuf
message C2S
{
    required Qot_Common.Security security = 1; // 股票
    optional int32 daysBefore             = 2; // 不填或 0=实时，N=取前第 N 个交易日的历史数据
}

message Request
{
    required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 买卖方向参见 [BuySellType](./quote.md#324)

* **返回**

```protobuf
message S2C
{
    optional bool       isRealTime   = 1; // true=实时数据，false=历史数据
    optional int64      dataTime     = 2; // 数据更新时间戳（秒）
    optional string     dataTimeStr  = 3; // 数据更新时间字符串，格式 YYYY-MM-DD HH:MM:SS
    repeated BrokerItem brokerList   = 4; // 经纪商列表，按净买/卖量从高到低排列
}

message Response
{
    required int32  retType = 1 [default = -400]; // 返回结果，详见 Common.RetType
    optional string retMsg  = 2;                  // 返回结果描述
    optional int32  errCode = 3;                  // 错误码
    optional S2C    s2c     = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)
>    - 买卖方向参见 [BuySellType](./quote.md#324)

* **Example**

```javascript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetTopTenBuySellBrokers(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {

            const req = {
                c2s: {
                    security: {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                },
            };
            websocket.GetTopTenBuySellBrokers(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("GetTopTenBuySellBrokers: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{
        websocket.stop();
        console.log("stop");
    }, 5000);
}
```

* **Output**

``` JavaScript
GetTopTenBuySellBrokers: errCode 0, retMsg , retType 0
{
  "isRealTime": true,
  "dataTime": "1778227221",
  "dataTimeStr": "2026-05-08 16:00:21",
  "brokerList": [{
    "netVol": "360300",
    "brokerName": "高盛",
    "buySellType": "BuySellType_NetBuy",
    "avgPrice": 471.037340153,
    "totalVol": 586500,
    "totalTurnover": 276263400
    //...
  }]
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 仅支持港股正股及基金。
* `days_before=0` 或不填返回实时数据（含均价/总量/总额），`days_before>0` 仅含净量和经纪商名称。
:::

---

# 获取每日卖空成交

`GetDailyShortVolume(req);`

* **介绍**

    获取每日卖空成交数据

* **参数**

```protobuf
message C2S
{
    required Qot_Common.Security security = 1; // 股票
    optional string nextKey               = 2; // 分页标识，首次不填，续拉时填上次返回的 nextKey；"-1" 表示无更多数据
    optional int32  num                   = 3; // 每页返回数量，默认 10，范围 1~50
}

message Request
{
    required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)

* **返回**

```protobuf
message S2C
{
    repeated UsDailyShortVolumeItem usItemList        = 1; // 美股每日卖空数据列表
    repeated HkDailyShortVolumeItem hkItemList        = 2; // 港股每日卖空数据列表
    optional string                 nextKey           = 3; // 分页标识，"-1" 表示无更多数据
    optional int64                  aggregatedShort   = 4; // 未平仓股数，仅港股
    optional double                 aggregatedShortRatio = 5; // 占流通股比例，百分号前的值，如 12.34 表示 12.34%，仅港股
    optional string                 newTimeStr        = 6; // 最新数据时间字符串，格式 YYYY-MM-DD，对应市场时区，仅港股
}

message Response
{
    required int32  retType = 1 [default = -400]; // 返回结果，详见 Common.RetType
    optional string retMsg  = 2;                  // 返回结果描述
    optional int32  errCode = 3;                  // 错误码
    optional S2C    s2c     = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

```javascript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetDailyShortVolume(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {

            const req = {
                c2s: {
                    security: {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                },
            };
            websocket.GetDailyShortVolume(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("GetDailyShortVolume: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{
        websocket.stop();
        console.log("stop");
    }, 5000);
}
```

* **Output**

``` JavaScript
GetDailyShortVolume: errCode 0, retMsg , retType 0
{
  "hkItemList": [{
    "timestamp": "1778169600",
    "timestampStr": "2026-05-08",
    "sharesTraded": "25207039",
    "turnover": 11871680730.68,
    "shortSellSharesTraded": "2464300",
    "shortSellTurnover": 1161032040,
    "openPrice": 475,
    "closePrice": 471.4,
    "lastClosePrice": 477.4,
    "dailyTradeAvgRatio": 11.36
    //...
  }],
  "nextKey": "1776960000",
  "aggregatedShort": "51480638",
  "aggregatedShortRatio": 0.56,
  "newTimeStr": "30/04/2026"
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持港股、美股正股及基金。
:::

---

# 获取空头持仓

`GetShortInterest(req);`

* **介绍**

    获取空头持仓数据

* **参数**

```protobuf
message C2S
{
    required Qot_Common.Security security = 1; // 股票
    optional string nextKey               = 2; // 分页标识，首次不填，续拉时填上次返回的 nextKey；"-1" 表示无更多数据
    optional int32  num                   = 3; // 每页返回数量，默认 10，范围 1~50
}

message Request
{
    required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)

* **返回**

```protobuf
message S2C
{
    repeated UsShortInterestItem usItemList = 1; // 美股空头持仓数据列表
    repeated HkShortInterestItem hkItemList = 2; // 港股空头持仓数据列表
    optional string              nextKey    = 3; // 分页标识，"-1" 表示无更多数据
}

message Response
{
    required int32  retType = 1 [default = -400]; // 返回结果，详见 Common.RetType
    optional string retMsg  = 2;                  // 返回结果描述
    optional int32  errCode = 3;                  // 错误码
    optional S2C    s2c     = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

```javascript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetShortInterest(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {

            const req = {
                c2s: {
                    security: {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                },
            };
            websocket.GetShortInterest(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("GetShortInterest: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{
        websocket.stop();
        console.log("stop");
    }, 5000);
}
```

* **Output**

``` JavaScript
GetShortInterest: errCode 0, retMsg , retType 0
{
  "hkItemList": [{
    "timestamp": "1777478400",
    "timestampStr": "2026-04-30",
    "closePrice": 467.8,
    "lastClosePrice": 479.2,
    "aggregatedShort": "51480638",
    "aggregatedShortRatio": 0.56
    //...
  }],
  "nextKey": "1772121600"
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 支持港股、美股正股及基金。
:::

---

# 获取期权链到期日

`GetOptionExpirationDate(req);`

* **介绍**

    通通过标的股票，查询期权链的所有到期日。如需获取完整期权链，请配合 [获取期权链](../quote/get-option-chain.md) 接口使用。

* **参数**

```protobuf
message C2S
{
	required Qot_Common.Security owner = 1; //期权标的股，目前仅支持传入港美正股以及恒指国指美指
	optional int32 indexOptionType = 2; //Qot_Common.IndexOptionType，指数期权的类型，仅用于恒指国指
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 指数期权类别枚举参见 [IndexOptionType](./quote.md#5149)

* **返回**

```protobuf
message OptionExpirationDate
{
	optional string strikeTime = 1; //期权链行权日（格式：yyyy-MM-dd，港股和 A 股市场默认是北京时间，美股市场默认是美东时间）
	optional double strikeTimestamp = 2; //行权日时间戳
	required int32 optionExpiryDateDistance = 3; //距离到期日天数，负数表示已过期
	optional int32 cycle = 4; //Qot_Common.ExpirationCycle,交割周期（支持香港指数期权、美股指数期权）
}
 
message S2C
{
	repeated OptionExpirationDate dateList = 1; //期权链行权日
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType,返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 期权交割周期枚举参见 [ExpirationCycle](./quote.md#2235)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetOptionExpirationDate(){
    const { RetType } = Common
    const { IndexOptionType, QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功

            const req = {
                c2s: {
                    owner:{
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                    indexOptionType: IndexOptionType.IndexOptionType_Unknown,
                },
            };

            websocket.GetOptionExpirationDate(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("OptionExpirationDate: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
OptionExpirationDate: errCode 0, retMsg , retType 0
{
  "dateList": [{
    "strikeTime": "2021-09-29",
    "strikeTimestamp": 1632844800,
    "optionExpiryDateDistance": 19
  }, {
    "strikeTime": "2021-10-28",
    "strikeTimestamp": 1635350400,
    "optionExpiryDateDistance": 48
  }, ..., {
    "strikeTime": "2022-09-29",
    "strikeTimestamp": 1664380800,
    "optionExpiryDateDistance": 384
  }]
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 60 次获取期权链到期日接口
:::

---

# 获取期权链

`GetOptionChain(req);`

* **介绍**

    通过标的股票查询期权链。此接口仅返回期权链的静态信息，如需获取报价或摆盘等动态信息，请用此接口返回的股票代码，自行 [订阅](../quote/sub.md) 所需要的类型。

* **参数**

```protobuf
enum OptionCondType
{
	OptionCondType_Unknow = 0;
	OptionCondType_WithIn = 1; //价内
	OptionCondType_Outside = 2; //价外
}

//以下为数据字段筛选，可选字段，不填表示不过滤
message DataFilter
{
	optional double impliedVolatilityMin = 1; //隐含波动率过滤起点（精确到小数点后 0 位，超出部分会被舍弃）
	optional double impliedVolatilityMax = 2; //隐含波动率过滤终点（精确到小数点后 0 位，超出部分会被舍弃）

	optional double deltaMin = 3; //希腊值 Delta 过滤起点（精确到小数点后 3 位，超出部分会被舍弃）
	optional double deltaMax = 4; //希腊值 Delta 过滤终点（精确到小数点后 3 位，超出部分会被舍弃）

	optional double gammaMin = 5; //希腊值 Gamma 过滤起点（精确到小数点后 3 位，超出部分会被舍弃）
	optional double gammaMax = 6; //希腊值 Gamma 过滤终点（精确到小数点后 3 位，超出部分会被舍弃）

	optional double vegaMin = 7; //希腊值 Vega 过滤起点（精确到小数点后 3 位，超出部分会被舍弃）
	optional double vegaMax = 8; //希腊值 Vega 过滤终点（精确到小数点后 3 位，超出部分会被舍弃）

	optional double thetaMin = 9; //希腊值 Theta 过滤起点（精确到小数点后 3 位，超出部分会被舍弃）
	optional double thetaMax = 10; //希腊值 Theta 过滤终点（精确到小数点后 3 位，超出部分会被舍弃）

	optional double rhoMin = 11; //希腊值 Rho 过滤起点（精确到小数点后 3 位，超出部分会被舍弃）
	optional double rhoMax = 12; //希腊值 Rho 过滤终点（精确到小数点后 3 位，超出部分会被舍弃）

	optional double netOpenInterestMin = 13; //净未平仓合约数过滤起点（精确到小数点后 0 位，超出部分会被舍弃）
	optional double netOpenInterestMax = 14; //净未平仓合约数过滤终点（精确到小数点后 0 位，超出部分会被舍弃）

	optional double openInterestMin = 15; //未平仓合约数过滤起点（精确到小数点后 0 位，超出部分会被舍弃）
	optional double openInterestMax = 16; //未平仓合约数过滤终点（精确到小数点后 0 位，超出部分会被舍弃）

	optional double volMin = 17; //成交量过滤起点（精确到小数点后 0 位，超出部分会被舍弃）
	optional double volMax = 18; //成交量过滤终点（精确到小数点后 0 位，超出部分会被舍弃）
}

message C2S
{
	required Qot_Common.Security owner = 1; //期权标的股，目前仅支持传入港美正股以及恒指国指美指
	optional int32 indexOptionType = 6; //Qot_Common.IndexOptionType，指数期权的类型，仅用于恒指国指
	optional int32 type = 2; //Qot_Common.OptionType，期权类型，可选字段，不指定则表示都返回
	optional int32 condition = 3; //OptionCondType，价内价外，可选字段，不指定则表示都返回
	required string beginTime = 4; //期权到期日开始时间（格式：yyyy-MM-dd）
	required string endTime = 5; //期权到期日结束时间，时间跨度最多一个月（格式：yyyy-MM-dd）
	optional DataFilter dataFilter = 7; //数据字段筛选
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 期权类型枚举参见 [OptionType](./quote.md#3713)
>    - 指数期权类别枚举参见 [IndexOptionType](./quote.md#5149)

* **返回**

```protobuf
message OptionItem
{
	optional Qot_Common.SecurityStaticInfo call = 1; //看涨期权，不一定有该字段，由请求条件决定
	optional Qot_Common.SecurityStaticInfo put = 2; //看跌期权，不一定有该字段，由请求条件决定
}

message OptionChain
{
	required string strikeTime = 1; //行权日（格式：yyyy-MM-dd）
	repeated OptionItem option = 2; //期权信息
	optional double strikeTimestamp = 3; //行权日时间戳
}

message S2C
{
	repeated OptionChain optionChain = 1; //期权链
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType，返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	optional S2C s2c = 4;
}
```
>    - 股票静态信息结构参见 [SecurityStaticInfo](./quote.md#609)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetOptionChain(){
    const { RetType } = Common
    const {  QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功

            const req = {
                c2s: {
                    owner:{
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                    beginTime: "2021-09-01",
                    endTime: "2021-09-30",
                },
            };

            websocket.GetOptionChain(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("OptionChain: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
OptionChain: errCode 0, retMsg , retType 0
{
  "optionChain": [{
    "strikeTime": "2021-09-29",
    "option": [{
      "call": {
        "basic": {
          "security": {
            "market": 1,
            "code": "TCH210929C300000"
          },
          "id": "80287116",
          "lotSize": 100,
          "secType": 8,
          "name": "腾讯 210929 300.00 购",
          "listTime": "",
          "delisting": false
        },
        "optionExData": {
          "type": 1,
          "owner": {
            "market": 1,
            "code": "00700"
          },
          "strikeTime": "2021-09-29",
          "strikePrice": 300,
          "suspend": false,
          "market": "",
          "strikeTimestamp": 1632844800,
          "expirationCycle": 1,
          "optionStandardType": 1,
          "optionSettlementMode": 2,
        }
      },
      "put": {
        "basic": {
          "security": {
            "market": 1,
            "code": "TCH210929P300000"
          },
          "id": "80287124",
          "lotSize": 100,
          "secType": 8,
          "name": "腾讯 210929 300.00 沽",
          "listTime": "",
          "delisting": false
        },
        "optionExData": {
          "type": 2,
          "owner": {
            "market": 1,
            "code": "00700"
          },
          "strikeTime": "2021-09-29",
          "strikePrice": 300,
          "suspend": false,
          "market": "",
          "strikeTimestamp": 1632844800,
          "expirationCycle": 1,
          "optionStandardType": 1,
          "optionSettlementMode": 2,
        }
      }
    }, ..., {
      "call": {
        "basic": {
          "security": {
            "market": 1,
            "code": "TCH210929C950000"
          },
          "id": "80215136",
          "lotSize": 100,
          "secType": 8,
          "name": "腾讯 210929 950.00 购",
          "listTime": "",
          "delisting": false
        },
        "optionExData": {
          "type": 1,
          "owner": {
            "market": 1,
            "code": "00700"
          },
          "strikeTime": "2021-09-29",
          "strikePrice": 950,
          "suspend": false,
          "market": "",
          "strikeTimestamp": 1632844800,
          "expirationCycle": 1,
          "optionStandardType": 1,
          "optionSettlementMode": 2,
        }
      },
      "put": {
        "basic": {
          "security": {
            "market": 1,
            "code": "TCH210929P950000"
          },
          "id": "80215157",
          "lotSize": 100,
          "secType": 8,
          "name": "腾讯 210929 950.00 沽",
          "listTime": "",
          "delisting": false
        },
        "optionExData": {
          "type": 2,
          "owner": {
            "market": 1,
            "code": "00700"
          },
          "strikeTime": "2021-09-29",
          "strikePrice": 950,
          "suspend": false,
          "market": "",
          "strikeTimestamp": 1632844800,
          "expirationCycle": 1,
          "optionStandardType": 1,
          "optionSettlementMode": 2,
        }
      }
    }],
    "strikeTimestamp": 1632844800
  }]
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 10 次获取期权链接口
* 传入的时间跨度上限为 30 天
:::

:::tip 提示
* 此接口不支持查询已过期的期权链，**结束日期** 参数请输入今天或未来的日期
* Open interest (OI) 数据每日更新，更新时点取决于具体交易所。美股期权在盘前时段更新，港股期权在盘后更新。
:::

---

# 获取期权波动率分析

`GetOptionVolatility(req);`

* **介绍**

    获取期权波动率分析数据

* **参数**

```protobuf
message C2S
{
    required Qot_Common.Security                      security        = 1; // 期权代码
    optional Qot_Common.OptionVolatilityTimePeriodType queryTimePeriod = 2; // 查询时间周期，详见 Qot_Common.OptionVolatilityTimePeriodType，不填默认 Month
    optional int32                                    hvTimePeriod    = 3; // 标的物历史波动率周期（5~250 日），不填默认 30 日
}

message Request
{
    required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)

* **返回**

```protobuf
message S2C
{
    repeated VolatilityItem                    itemList       = 1; // 波动率数据列表，时间按从大到小排序
    optional double                            averageImpvol  = 2; // 隐含波动率综合值（均值，百分号前的值）
    optional Qot_Common.OptionImpvolStatusType impvolStatus   = 3; // 波动率状态，详见 Qot_Common.OptionImpvolStatusType
    optional string                            analysis       = 4; // 分析文案
}

message Response
{
    required int32  retType = 1 [default = -400]; // 返回结果，详见 Common.RetType
    optional string retMsg  = 2;                  // 返回结果描述
    optional int32  errCode = 3;                  // 错误码
    optional S2C    s2c     = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)
>    - 查询时间周期参见 [OptionVolatilityTimePeriodType](./quote.md#8366)
>    - 波动率状态参见 [OptionImpvolStatusType](./quote.md#5480)

* **Example**

```javascript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetOptionVolatility(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {

            const req = {
                c2s: {
                    security: {
                        market: QotMarket.QotMarket_US_Security,
                        code: "AAPL281215C320000",
                    },
                },
            };
            websocket.GetOptionVolatility(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("GetOptionVolatility: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{
        websocket.stop();
        console.log("stop");
    }, 5000);
}
```

* **Output**

```javascript
GetOptionVolatility: errCode 0, retMsg , retType 0
{
  "itemList": [{
    "timestamp": "1776052800",
    "timestampStr": "2026-04-13",
    "impliedVolatility": 27.813,
    "historyVolatility": 18.957,
    "volatilityPremium": 8.856
    //...
  }],
  "averageImpvol": 28.127,
  "impvolStatus": "ImpvolFluctuating",
  "analysis": "近1月100.00%的时刻，该期权的隐含波动率大于历史波动率；\n隐含波动率的均值为28.13%，大于该期权当前的隐含波动率27.72%；\n波动率溢价：最大值为+8.86%，最小值为+2.46%，当前值+2.46%超过了周期内0.00%的时刻；"
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 仅支持期权合约代码，不支持正股代码。
:::

---

# 获取期权行权概率

`GetOptionExerciseProbability(req);`

* **介绍**

    获取期权行权概率数据

* **参数**

```protobuf
message C2S
{
    required Qot_Common.Security security = 1; // 期权代码
}

message Request
{
    required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)

* **返回**

```protobuf
message S2C
{
    repeated StrikeProbabilityItem itemList = 1; // 行权概率列表，时间按从大到小排序
}

message Response
{
    required int32  retType = 1 [default = -400]; // 返回结果，详见 Common.RetType
    optional string retMsg  = 2;                  // 返回结果描述
    optional int32  errCode = 3;                  // 错误码
    optional S2C    s2c     = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

```javascript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetOptionExerciseProbability(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {

            const req = {
                c2s: {
                    security: {
                        market: QotMarket.QotMarket_US_Security,
                        code: "AAPL281215C320000",
                    },
                },
            };
            websocket.GetOptionExerciseProbability(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("GetOptionExerciseProbability: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{
        websocket.stop();
        console.log("stop");
    }, 5000);
}
```

* **Output**

``` JavaScript
GetOptionExerciseProbability: errCode 0, retMsg , retType 0
{
  "itemList": [{
    "timestamp": "1778422150",
    "timestampStr": "2026-05-10",
    "securityPrice": 293.32,
    "strikeProbability": 41.875
    //...
  }]
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
* 仅支持期权合约代码，不支持正股代码。
:::

---

# 获取期权策略

`GetOptionStrategy(req);`

* **介绍**

    获取期权策略数据

* **参数**

```protobuf
message C2S
{
	required Qot_Common.Security owner = 1;      //期权标的股，目前仅支持港美正股以及恒指国指
	required int32 option_strategy = 2;          //OptionStrategyType，期权策略类型
	optional string expire_time = 3;             //到期日（近端），格式 yyyy-MM-dd，不填表示不过滤到期日
	optional string far_expire_time = 4;         //远端到期日，对角策略（DiagonalSpread）时使用
	optional double spread = 5;                  //价差筛选值，垂直策略、宽跨式、领式、蝶式、鹰式、铁蝶式、铁鹰式、对角等策略需要
	optional int32 option_type = 6;              //OptionType，期权类型，不填表示都返回
	optional double strike_price = 7;            //行权价筛选，不填表示返回所有
	optional int32 index_option_type = 8;        //IndexOptionType，指数期权类型，仅用于恒指国指
	optional Qot_Common.QotHeader header = 100;  //行情公共参数头
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 期权策略类型枚举参见 [OptionStrategyType](./quote.md#2931)
>    - 指数期权类别枚举参见 [IndexOptionType](./quote.md#5149)
>    - 期权类型枚举参见 [OptionType](./quote.md#3713)

* **返回**

```protobuf
message OptionStrategyItem
{
	required string code = 1;                     //组合策略代码
	required string name = 2;                     //组合策略名称
	required int32 option_strategy = 3;           //OptionStrategyType，组合策略类型
	required Qot_Common.Security stock_owner = 4; //标的股
	repeated Qot_Common.ComboLeg multi_legs = 5;  //组合子订单列表
}

message S2C
{
	repeated OptionStrategyItem strategyList = 1; //期权策略组合列表
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType，返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)
>    - 期权策略类型枚举参见 [OptionStrategyType](./quote.md#2931)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetOptionStrategy(){
    const { RetType } = Common
    const { QotMarket, OptionStrategyType } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功
            const req = {
                c2s: {
                    owner: { market: QotMarket.QotMarket_HK_Security, code: "00700" },
                    optionStrategy: OptionStrategyType.OptionStrategyType_Straddle, // 跨式策略
                },
            };

            websocket.GetOptionStrategy(req)
            .then((res) => {
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetOptionStrategy: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
GetOptionStrategy: errCode 0, retMsg , retType 0
{
  "strategyList": [{
    "code": "TCH260522C/P330",
    "name": "腾讯 跨式策略",
    "optionStrategy": 6,
    "stockOwner": {
      "market": 1,
      "code": "00700"
    },
    "multiLegs": [{
      "security": { "market": 1, "code": "TCH260522P330000" },
      "side": 1,
      "qtyRatio": 1
    }, {
      "security": { "market": 1, "code": "TCH260522C330000" },
      "side": 1,
      "qtyRatio": 1
    }]
  }, ...]
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
:::

---

# 获取有效价差

`GetOptionStrategySpread(req);`

* **介绍**

    获取期权策略有效价差列表

* **参数**

```protobuf
message C2S
{
	required Qot_Common.Security owner = 1;      //期权标的股，目前仅支持港美正股以及恒指国指
	required int32 option_strategy = 2;          //OptionStrategyType，期权策略类型
	optional string expire_time = 3;             //到期日（近端），格式 yyyy-MM-dd，不填表示取第一条
	optional string far_expire_time = 4;         //远端到期日，对角策略（DiagonalSpread）时必传
	optional int32 index_option_type = 5;        //IndexOptionType，指数期权类型，仅用于恒指国指
	optional Qot_Common.QotHeader header = 100;  //行情公共参数头
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 期权策略类型枚举参见 [OptionStrategyType](./quote.md#2931)
>    - 指数期权类别枚举参见 [IndexOptionType](./quote.md#5149)
>    - 仅支持 Spread、Strangle、Collar、Butterfly、Condor、IronButterfly、IronCondor、DiagonalSpread 等策略查询有效价差

* **返回**

```protobuf
message S2C
{
	repeated double spreadList = 1; //有效价差列表，如 [0.5, 1.0, 2.0]，单位与正股价格一致
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType，返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetOptionStrategySpread(){
    const { RetType } = Common
    const { QotMarket, OptionStrategyType } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功
            const req = {
                c2s: {
                    owner: { market: QotMarket.QotMarket_HK_Security, code: "00700" },
                    optionStrategy: OptionStrategyType.OptionStrategyType_Strangle, // 宽跨式策略
                },
            };

            websocket.GetOptionStrategySpread(req)
            .then((res) => {
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetOptionStrategySpread: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
GetOptionStrategySpread: errCode 0, retMsg , retType 0
{
  "spreadList": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260]
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次。
:::

---

# 期权损益分析

`GetOptionStrategyAnalysis(req);`

* **介绍**

    期权组合损益分析

* **参数**

```protobuf
message C2S
{
	repeated Qot_Common.ComboLeg multi_legs = 1; //组合策略合约腿列表，至少传入 1 条
	optional Qot_Common.QotHeader header = 100;  //行情公共参数头
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 组合腿 multiLegs 可由 [GetOptionStrategy](./get-option-strategy.md) 返回的 multiLegs 获得

* **返回**

```protobuf
message S2C
{
	required string code = 1;            //组合策略代码
	required string name = 2;            //组合策略名称
	required int32 option_strategy = 3;  //OptionStrategyType，组合策略类型
	optional double bid1 = 4;            //买一价
	optional double ask1 = 5;            //卖一价
	optional double max_profit = 6;      //最大盈利，无上限时为极大值
	optional double max_loss = 7;        //最大亏损，无下限时为极小值
	repeated double breakeven_points = 8;//盈亏平衡点列表，可能有多个
	optional double prob_of_profit = 9;  //盈利概率
	optional double delta = 10;          //组合 Delta
	optional double theta = 11;          //组合 Theta（每日时间价值损耗）
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType，返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)
>    - 期权策略类型枚举参见 [OptionStrategyType](./quote.md#2931)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetOptionStrategyAnalysis(){
    const { RetType } = Common
    const { QotMarket, OptionStrategyType } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功
            // 先获取期权策略，取其中一组组合腿
            websocket.GetOptionStrategy({
                c2s: {
                    owner: { market: QotMarket.QotMarket_HK_Security, code: "00700" },
                    optionStrategy: OptionStrategyType.OptionStrategyType_Straddle,
                },
            })
            .then((res) => {
                let { retType, s2c: { strategyList } } = res
                if(retType == RetType.RetType_Succeed && strategyList.length > 0){
                    const req = {
                        c2s: {
                            multiLegs: strategyList[0].multiLegs,
                        },
                    };

                    websocket.GetOptionStrategyAnalysis(req)
                    .then((res) => {
                        let { errCode, retMsg, retType, s2c } = res
                        console.log("GetOptionStrategyAnalysis: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                        if(retType == RetType.RetType_Succeed){
                            let data = beautify(JSON.stringify(s2c), {
                                indent_size: 2,
                                space_in_empty_paren: true,
                            });
                            console.log(data);
                        }
                    })
                    .catch((error) => {
                        console.log("error:", error);
                    });
                }
            })
            .catch((error) => {
                console.log("GetOptionStrategy error:", error);
            });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
GetOptionStrategyAnalysis: errCode 0, retMsg , retType 0
{
  "code": "TCH260522C/P330",
  "name": "腾讯 跨式策略",
  "optionStrategy": 6,
  "bid1": 0,
  "ask1": 130.44,
  "maxProfit": 1000000000000000,
  "maxLoss": -13044,
  "breakevenPoints": [199.56, 460.44],
  "probOfProfit": 0.315492,
  "delta": 0.974369,
  "theta": -0.785757
}
stop
```

:::tip 接口限制
* 不占用期权订阅额度。
* 每 30 秒内最多请求 30 次。
:::

---

# 获取期权快照

`GetOptionQuote(req);`

* **介绍**

    获取期权组合快照行情

* **参数**

```protobuf
message C2S
{
	repeated Qot_Common.ComboLeg multi_legs = 1; //组合策略合约腿列表
	optional Qot_Common.QotHeader header = 100;  //行情公共参数头
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 组合腿 multiLegs 可由 [GetOptionStrategy](./get-option-strategy.md) 返回的 multiLegs 获得

* **返回**

```protobuf
message OptionQuote
{
	optional double price = 1;                //最新价
	optional double chg = 2;                  //涨跌额
	optional double chg_rate = 3;             //涨跌幅（百分比）
	optional int64  vol = 4;                  //成交量
	optional double turnover = 5;             //成交额
	optional double high = 6;                 //最高价
	optional double low = 7;                  //最低价
	optional double mid = 8;                  //中间价
	optional double open = 9;                 //今开
	optional double pre_close = 10;           //昨收
	optional int32  open_interest = 11;       //未平仓合约数
	optional double premium = 12;             //溢价（百分比）
	optional double IV = 13;                  //隐含波动率（百分比）
	optional double delta = 14;               //Delta
	optional double gamma = 15;               //Gamma
	optional double vega = 16;                //Vega
	optional double theta = 17;               //Theta
	optional double rho = 18;                 //Rho
	optional int32  option_type = 19;         //OptionType，CALL/PUT
	optional string expire_time = 20;         //到期日
	optional double strike = 21;              //行权价
	optional double contract_size = 22;       //合约规模
	optional double contract_multiplier = 23; //合约乘数
	optional int32  exercise_type = 24;       //行权类型
	optional int32  days_to_expiry = 25;      //距到期天数
	optional int32  net_open_interest = 26;   //净未平仓合约数
	optional double contract_value = 27;      //合约金额
	optional double equal_underlying = 28;    //相当正股手数
	optional int32  index_option_type = 29;   //指数期权类型
	optional double intrinsic_value = 30;     //内在价值
	optional double time_value = 31;          //时间价值
	repeated double breakeven_point = 32;     //盈亏平衡点列表
	repeated double dist_to_breakeven = 33;   //与盈亏平衡点的距离
	optional double prob_of_profit = 34;      //盈利概率
	optional double seller_roi = 35;          //卖方回报率（百分比）
	optional double mark_price = 36;          //标记价
	optional double leverage_ratio = 37;      //杠杆倍数
	optional double effective_gearing = 38;   //有效杠杆
}

message S2C
{
	repeated OptionQuote optionQuoteList = 1; //期权实时行情列表
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType，返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetOptionQuote(){
    const { RetType } = Common
    const { QotMarket, OptionStrategyType } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功
            // 先获取期权策略，取其中一组组合腿
            websocket.GetOptionStrategy({
                c2s: {
                    owner: { market: QotMarket.QotMarket_HK_Security, code: "00700" },
                    optionStrategy: OptionStrategyType.OptionStrategyType_Straddle,
                },
            })
            .then((res) => {
                let { retType, s2c: { strategyList } } = res
                if(retType == RetType.RetType_Succeed && strategyList.length > 0){
                    const req = {
                        c2s: {
                            multiLegs: strategyList[0].multiLegs,
                        },
                    };

                    websocket.GetOptionQuote(req)
                    .then((res) => {
                        let { errCode, retMsg, retType, s2c } = res
                        console.log("GetOptionQuote: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                        if(retType == RetType.RetType_Succeed){
                            let data = beautify(JSON.stringify(s2c), {
                                indent_size: 2,
                                space_in_empty_paren: true,
                            });
                            console.log(data);
                        }
                    })
                    .catch((error) => {
                        console.log("error:", error);
                    });
                }
            })
            .catch((error) => {
                console.log("GetOptionStrategy error:", error);
            });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
GetOptionQuote: errCode 0, retMsg , retType 0
{
  "optionQuoteList": [{
    "price": 131.65,
    "chg": 0,
    "chgRate": 0,
    "delta": 0.974369,
    "gamma": 0.000797,
    "vega": 0.019825,
    "theta": -0.785757,
    "rho": 0.016246,
    "expireTime": "2026-05-22",
    "contractSize": 100,
    "contractMultiplier": 100,
    "daysToExpiry": 2,
    "intrinsicValue": 125.2,
    "timeValue": 6.45,
    "breakevenPoint": [199.56, 460.44],
    "distToBreakeven": [255.64, -5.24],
    "probOfProfit": 0.315418,
    "markPrice": 130.4
  }]
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 120 次。
:::

---

# 筛选期权

`GetOptionScreen(req);`


* **介绍**

    期权选股

* **参数**

```protobuf
message Boundary
{
    required double value = 1;
    optional bool includes = 2;     // 是否闭区间，默认 true
}

message ValueInterval
{
    optional Boundary filterMin = 1;
    optional Boundary filterMax = 2;
}

message OptionIndicatorValue
{
    repeated int32 valueList = 1;       // 确切值列表 (用于 OPTION_TYPE 等)
    optional ValueInterval valueInterval = 2;   // 区间筛选
}

message PlateInfo
{
    repeated string plateIdList = 1;
    optional string parentPlateId = 2;
}

// 标的属性筛选条件
message UnderlyingFilter
{
    required int32 indicatorType = 1;           // OptUnderlyingIndicator
    optional OptionIndicatorValue indicatorValue = 2;
    repeated PlateInfo plateList = 3;           // 仅 PLATE(103) 时使用
}

// 期权属性筛选条件
message OptionFilter
{
    required int32 indicatorType = 1;           // OptIndicator
    optional OptionIndicatorValue indicatorValue = 2;
}

// 一组筛选条件：组内 OR，组间 AND；同一组内不能同时筛选标的属性（underlying）与期权属性（option）
message FilterGroup
{
    repeated UnderlyingFilter underlyingList = 1;
    repeated OptionFilter optionList = 2;
}

message Sort
{
    required int32 indicatorType = 1;
    required int32 direction = 2;               // 0=升序, 1=降序
}

message C2S
{
    repeated int32 marketCategoryList = 1;      // OptMarketCategory：US_STOCK=0、US_INDEX=1、US_FUTURE=2、HK_STOCK=3、HK_INDEX=4、JP_STOCK=5、JP_INDEX=6
    repeated FilterGroup filterList = 2;
    repeated Sort sortList = 3;
    optional int32 pageFrom = 4;
    optional int32 pageCount = 5;
    repeated int32 optionRetrieveList = 6;      // 声明要返回的期权字段，不传则返回默认基础字段
    repeated int32 underlyingRetrieveList = 7;  // 声明要返回的标的字段
}

message Request
{
    required C2S c2s = 1;
}
```

* **返回**

```protobuf
message Security
{
    required int32 market = 1;
    required string code = 2;
}

message UnderlyingInfo
{
    optional int64 stockID = 1;
    optional double iv = 2;
    optional double hv = 3;
    optional double ivRank = 4;
    optional double ivPercentile = 5;
    optional double marketCap = 6;
    optional double price = 7;
    optional double changeRatio = 8;
}

message OptionScreenItem
{
    optional Security security = 1;
    optional string optionName = 2;
    optional double strikePrice = 3;
    optional string strikeDate = 4;
    optional int32 optionType = 5;
    optional int32 exerciseType = 6;
    optional int32 expirationType = 7;
    optional bool inTheMoney = 8;
    optional int32 leftDay = 9;
    optional double price = 20;
    optional double midPrice = 21;
    optional double bidPrice = 22;
    optional double askPrice = 23;
    optional double bidAskSpread = 24;
    optional int64 bidVolume = 25;
    optional int64 askVolume = 26;
    optional double bidAskVolumeRatio = 27;
    optional double changeRatio = 28;
    optional int64 volume = 29;
    optional double turnover = 30;
    optional int64 openInterest = 31;
    optional double openInterestMarketCap = 32;
    optional double volOIRatio = 33;
    optional double premium = 34;
    optional double impliedVolatility = 40;
    optional double historyVolatility = 41;
    optional double ivHvRatio = 42;
    optional double delta = 43;
    optional double gamma = 44;
    optional double vega = 45;
    optional double theta = 46;
    optional double rho = 47;
    optional double leverageRatio = 48;
    optional double effectiveGearing = 49;
    optional UnderlyingInfo underlyingInfo = 50;
    optional double itmProbability = 51;
    optional double buyToBep = 52;
    optional double sellToBep = 53;
    optional double buyProfitProbability = 54;
    optional double sellProfitProbability = 55;
    optional double intrinsicValuePer = 56;
    optional double timeValuePer = 57;
    optional double itmDegree = 58;
    optional double otmDegree = 59;
    optional double otmProbability = 60;
    optional double sellAnnualizedReturn = 61;
    optional double intervalReturn = 62;
}

message S2C
{
    required bool lastPage = 1;
    required int32 allCount = 2;
    repeated OptionScreenItem dataList = 3;
}

message Response
{
    required int32 retType = 1 [default = -400];
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3253

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetOptionScreen(){
    const { RetType } = Common
    const { QotMarket, MarketCategory, OptionIndicatorType } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            // 筛选美股股票期权：CALL、价内、Delta 0.5~0.7，按 Delta 升序取回前 10 条
            const req = {
                c2s: {
                    marketCategoryList: [MarketCategory.MarketCategory_US_Stock],
                    filterList: [
                        {
                            optionList: [
                                { indicatorType: OptionIndicatorType.OptionIndicatorType_OptionType, indicatorValue: { valueList: [1] } },
                                { indicatorType: OptionIndicatorType.OptionIndicatorType_InTheMoney, indicatorValue: { valueList: [1] } },
                                { indicatorType: OptionIndicatorType.OptionIndicatorType_Delta, indicatorValue: { valueInterval: { filterMin: { value: 0.5, includes: true }, filterMax: { value: 0.7, includes: true } } } }
                            ]
                        }
                    ],
                    sortList: [
                        { indicatorType: OptionIndicatorType.OptionIndicatorType_Delta, direction: 0 }
                    ],
                    pageFrom: 0,
                    pageCount: 10,
                    optionRetrieveList: [
                        OptionIndicatorType.OptionIndicatorType_StrikePrice,
                        OptionIndicatorType.OptionIndicatorType_LeftDay,
                        OptionIndicatorType.OptionIndicatorType_Delta,
                        OptionIndicatorType.OptionIndicatorType_ImpliedVolatility
                    ],
                },
            };
            websocket.GetOptionScreen(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetOptionScreen: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetOptionScreen()
```

* **Output**

``` JavaScript
GetOptionScreen: errCode 0, retMsg , retType 0
{
  "lastPage": true,
  "allCount": 1,
  "dataList": [
    {
      "security": { "market": 11, "code": "AAPL260529C00225000" },
      "optionName": "AAPL 260529 225 CALL",
      "strikePrice": 225,
      "strikeDate": 20260529,
      "optionType": 1,
      "exerciseType": 1,
      "expirationType": 2,
      "inTheMoney": 1,
      "leftDay": 342,
      "price": 12.5,
      "midPrice": 12.525,
      "bidPrice": 12.4,
      "askPrice": 12.65,
      "bidAskSpread": 0.25,
      "bidVolume": 25,
      "askVolume": 40,
      "changeRate": 1.2,
      "volume": 152,
      "turnover": 1900000,
      "openInterest": 8530,
      "bidAskVolumeRatio": 1.6,
      "openInterestMarketCap": 1919250,
      "volOIRatio": 0.0178,
      "premium": 12.5,
      "impliedVolatility": 28.5,
      "delta": 0.62,
      "gamma": 0.015,
      "vega": 0.18,
      "theta": -0.05,
      "rho": 0.02,
      "leverageRatio": 18,
      "effectiveGearing": 11.16,
      "itmProbability": 68.5,
      "underlyingInfo": { "stockID": "6977384", "price": 225.0, "changeRate": 1.2, "marketCap": 3450000000000 }
    }
  ]
}
```

:::tip 接口限制
* 每 30 秒内最多请求 10 次筛选期权接口
:::

---

# 期权市场统计

`getOptionMarketStatistic(qotGetOptionMarketStatistic)`


* **介绍**

    获取期权市场统计数据

* **参数**

```protobuf
message C2S
{
    required int32 optionMarket = 1; //Qot_OptionCommon.OptionMarket，期权市场类型
    required int32 dataType = 2; //Qot_OptionCommon.OptionStatisticDataType，数据类型（成交量或持仓量）
    required string beginTime = 3; //开始时间字符串
    required string endTime = 4; //结束时间字符串，时间跨度超过一年时自动分页
    optional bytes nextPageKey = 5; //分页请求的key，首页不填，续页填入上一页返回的nextPageKey
}

message Request
{
    required C2S c2s = 1;
}
```

* **返回**

```protobuf
//每日统计数据
message StatisticItem
{
    required string time = 1; //交易日时间字符串
    optional double timestamp = 2; //交易日时间戳
    required int64 callValue = 3; //看涨期权合计值（成交量或持仓量，由请求的dataType决定）
    required int64 putValue = 4; //看跌期权合计值
    optional int64 totalValue = 5; //总值（callValue + putValue）
    optional double ratio = 6; //Put/Call比值（callValue为0时不设置）
}

message S2C
{
    required int32 optionMarket = 1; //Qot_OptionCommon.OptionMarket，期权市场类型
    required int32 dataType = 2; //Qot_OptionCommon.OptionStatisticDataType，数据类型
    repeated StatisticItem statisticList = 3; //统计数据列表，按交易日降序排列
    optional bytes nextPageKey = 4; //分页请求的key，有值表示还有更多数据
}

message Response
{
    required int32 retType = 1 [default = -400]; //RetType，返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3301

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_OptionCommon } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetOptionMarketStatistic(){
    const { RetType } = Common
    const { OptionMarket, OptionStatisticDataType } = Qot_OptionCommon
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11112, false, ''];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: {
                    optionMarket: OptionMarket.OptionMarket_US_Security,
            dataType: OptionStatisticDataType.OptionStatisticDataType_Volume,
            beginTime: '2026-06-01',
            endTime: '2026-06-15',
                },
            };
            websocket.GetOptionMarketStatistic(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetOptionMarketStatistic: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetOptionMarketStatistic()
```

* **Output**

``` JavaScript
GetOptionMarketStatistic: errCode 0, retMsg , retType 0
{
  "optionMarket": 1,
  "dataType": 0,
  "statisticList": [
    {
      "time": "2026-06-12",
      "timestamp": 1781237000,
      "callValue": 45658870,
      "putValue": 28723978,
      "totalValue": 74382848,
      "ratio": 0.6291
    },
    {
      "time": "2026-06-11",
      "timestamp": 1781150000,
      "callValue": 38303062,
      "putValue": 30520043,
      "totalValue": 68823105,
      "ratio": 0.796804
    },
    {
      "time": "2026-06-10",
      "timestamp": 1781064000,
      "callValue": 35371830,
      "putValue": 30180004,
      "totalValue": 65551834,
      "ratio": 0.853221
    }
  ]
}
```

:::tip 接口限制
* 30 秒内最多请求 60 次期权市场统计接口（支持分页的接口，仅首次调用纳入统计）
:::

---

# 期权标的总览

`getOptionUnderlyingOverview(qotGetOptionUnderlyingOverview)`


* **介绍**

    获取期权标的总览数据

* **参数**

```protobuf
message C2S
{
    repeated Qot_Common.Security ownerList = 1; //期权标的股列表，最多500个
    optional int32 indexOptionType = 2; //Qot_Common.IndexOptionType，指数期权的类型，仅用于恒指国指
}

message Request
{
    required C2S c2s = 1;
}
```

* **返回**

```protobuf
message HVItem
{
    required int32 timeRange = 1; //Qot_OptionCommon.OptionHVTimeRange，HV时间范围
    required double hv = 2; //历史波动率（百分比）
    optional double hvPercentile = 3; //HV百分位（百分比）
}

message UnderlyingData
{
    required Qot_Common.Security owner = 1; //期权标的股
    optional string code = 2; //股票代码
    optional string name = 3; //标的名称
    optional int64 callVolume = 4; //看涨期权成交量
    optional int64 putVolume = 5; //看跌期权成交量
    optional int64 callOpenInterest = 6; //看涨期权持仓量（T-1延迟）
    optional int64 putOpenInterest = 7; //看跌期权持仓量（T-1延迟）
    optional double iv = 8; //隐含波动率（百分比）
    optional double ivRank = 9; //IV排名百分位（百分比）
    optional double ivPercentile = 10; //IV百分位（百分比）
    repeated HVItem hvList = 11; //历史波动率列表（多个时间范围）
    optional double preIV = 12; //前一交易日IV（百分比）
}

message S2C
{
    repeated UnderlyingData underlyingDataList = 1; //标的最新数据列表
}

message Response
{
    required int32 retType = 1 [default = -400]; //RetType，返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3303

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetOptionUnderlyingOverview(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11112, false, ''];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: {
                    ownerList: [
                { market: QotMarket.QotMarket_US_Security, code: 'AAPL' },
                { market: QotMarket.QotMarket_US_Security, code: 'TSLA' },
            ],
                },
            };
            websocket.GetOptionUnderlyingOverview(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetOptionUnderlyingOverview: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetOptionUnderlyingOverview()
```

* **Output**

``` JavaScript
GetOptionUnderlyingOverview: errCode 0, retMsg , retType 0
{
  "underlyingDataList": [
    {
      "owner": { "market": 1, "code": "AAPL" },
      "code": "US.AAPL",
      "name": "Apple",
      "callVolume": 782941,
      "putVolume": 490299,
      "callOpenInterest": 3165108,
      "putOpenInterest": 2237950,
      "iv": 25.126,
      "ivRank": 37.702,
      "ivPercentile": 19.841,
      "hvList": [
        { "timeRange": 1, "hv": 23.324, "hvPercentile": 59.126 },
        { "timeRange": 2, "hv": 24.641, "hvPercentile": 65.476 },
        { "timeRange": 3, "hv": 23.019, "hvPercentile": 46.825 }
      ],
      "preIV": 25.617
    },
    {
      "owner": { "market": 1, "code": "TSLA" },
      "code": "US.TSLA",
      "name": "Tesla",
      "callVolume": 2197764,
      "putVolume": 1425740,
      "callOpenInterest": 4178685,
      "putOpenInterest": 2909774,
      "iv": 55.053,
      "ivRank": 39.265,
      "ivPercentile": 64.285,
      "hvList": [
        { "timeRange": 1, "hv": 49.359, "hvPercentile": 68.254 },
        { "timeRange": 2, "hv": 46.536, "hvPercentile": 58.73 },
        { "timeRange": 3, "hv": 44.99, "hvPercentile": 46.031 }
      ],
      "preIV": 55.401
    }
  ]
}
```

:::tip 接口限制
* 30 秒内最多请求 60 次期权标的总览接口
:::

---

# 期权标的历史统计

`getOptionUnderlyingHisStatistic(qotGetOptionUnderlyingHisStatistic)`


* **介绍**

    获取期权标的历史统计数据

* **参数**

```protobuf
message C2S
{
    required Qot_Common.Security owner = 1; //期权标的股
    optional int32 indexOptionType = 2; //Qot_Common.IndexOptionType
    required string beginTime = 3; //开始时间字符串
    required string endTime = 4; //结束时间字符串
    optional bytes nextPageKey = 5; //分页请求的key
}

message Request
{
    required C2S c2s = 1;
}
```

* **返回**

```protobuf
message DailyStatistic
{
    required string time = 1; //交易日时间字符串
    optional double timestamp = 2; //交易日时间戳
    optional int64 optionVolume = 3; //期权总成交量
    required int64 callVolume = 4; //看涨期权成交量
    required int64 putVolume = 5; //看跌期权成交量
    optional double putCallVolumeRatio = 6; //Put/Call成交量比
    optional int64 optionOpenInterest = 7; //期权总持仓量
    required int64 callOpenInterest = 8; //看涨期权持仓量
    required int64 putOpenInterest = 9; //看跌期权持仓量
    optional double putCallOpenInterestRatio = 10; //Put/Call持仓量比
    optional double underlyingPrice = 11; //标的价格
}

message S2C
{
    required Qot_Common.Security owner = 1; //期权标的股
    optional string code = 2; //股票代码
    optional string name = 3; //股票名称
    repeated DailyStatistic statisticList = 4; //统计数据列表，按交易日降序
    optional bytes nextPageKey = 5; //分页请求的key
}

message Response
{
    required int32 retType = 1 [default = -400]; //RetType，返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3302

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetOptionUnderlyingHisStatistic(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11112, false, ''];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: {
                    owner: { market: QotMarket.QotMarket_US_Security, code: 'AAPL' },
            beginTime: '2026-06-01',
            endTime: '2026-06-15',
                },
            };
            websocket.GetOptionUnderlyingHisStatistic(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetOptionUnderlyingHisStatistic: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetOptionUnderlyingHisStatistic()
```

* **Output**

``` JavaScript
GetOptionUnderlyingHisStatistic: errCode 0, retMsg , retType 0
{
  "owner": { "market": 1, "code": "AAPL" },
  "code": "US.AAPL",
  "name": "Apple",
  "statisticList": [
    {
      "time": "2026-06-12",
      "timestamp": 1781237000,
      "optionVolume": 1273240,
      "callVolume": 782941,
      "putVolume": 490299,
      "putCallVolumeRatio": 0.626227,
      "callOpenInterest": 0,
      "putOpenInterest": 0,
      "underlyingPrice": 291.13
    },
    {
      "time": "2026-06-11",
      "timestamp": 1781150000,
      "optionVolume": 950737,
      "callVolume": 580535,
      "putVolume": 370202,
      "putCallVolumeRatio": 0.637691,
      "optionOpenInterest": 5403058,
      "callOpenInterest": 3165108,
      "putOpenInterest": 2237950,
      "putCallOpenInterestRatio": 0.707069,
      "underlyingPrice": 295.63
    }
  ]
}
```

:::tip 接口限制
* 30 秒内最多请求 60 次期权标的历史统计接口（支持分页的接口，仅首次调用纳入统计）
:::

---

# 期权标的历史波动率

`getOptionUnderlyingHisVolatility(qotGetOptionUnderlyingHisVolatility)`


* **介绍**

    获取期权标的历史波动率数据

* **参数**

```protobuf
message C2S
{
    required Qot_Common.Security owner = 1; //期权标的股
    optional int32 indexOptionType = 2; //Qot_Common.IndexOptionType
    required string beginTime = 3; //开始时间字符串
    required string endTime = 4; //结束时间字符串
    optional bytes nextPageKey = 5; //分页请求的key
}

message Request
{
    required C2S c2s = 1;
}
```

* **返回**

```protobuf
message VolatilityItem
{
    required string time = 1; //交易日时间字符串
    optional double timestamp = 2; //交易日时间戳
    optional double iv = 3; //隐含波动率（百分比）
    optional double hv = 4; //历史波动率（百分比）
    optional double underlyingPrice = 5; //标的收盘价
}

message S2C
{
    required Qot_Common.Security owner = 1; //期权标的股
    optional string code = 2; //股票代码
    optional string name = 3; //股票名称
    repeated VolatilityItem volatilityList = 4; //波动率数据列表，按交易日降序
    optional bytes nextPageKey = 5; //分页请求的key
}

message Response
{
    required int32 retType = 1 [default = -400]; //RetType，返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3304

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetOptionUnderlyingHisVolatility(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11112, false, ''];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: {
                    owner: { market: QotMarket.QotMarket_US_Security, code: 'AAPL' },
            beginTime: '2026-06-01',
            endTime: '2026-06-15',
                },
            };
            websocket.GetOptionUnderlyingHisVolatility(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetOptionUnderlyingHisVolatility: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetOptionUnderlyingHisVolatility()
```

* **Output**

``` JavaScript
GetOptionUnderlyingHisVolatility: errCode 0, retMsg , retType 0
{
  "owner": { "market": 1, "code": "AAPL" },
  "code": "US.AAPL",
  "name": "Apple",
  "volatilityList": [
    { "time": "2026-06-12", "timestamp": 1781237000, "iv": 25.126, "hv": 23.324, "underlyingPrice": 291.13 },
    { "time": "2026-06-11", "timestamp": 1781150000, "iv": 25.617, "hv": 23.27, "underlyingPrice": 295.63 },
    { "time": "2026-06-10", "timestamp": 1781064000, "iv": 27.384, "hv": 22.892, "underlyingPrice": 291.58 },
    { "time": "2026-06-09", "timestamp": 1780978000, "iv": 27.237, "hv": 22.854, "underlyingPrice": 290.55 },
    { "time": "2026-06-08", "timestamp": 1780891000, "iv": 26.368, "hv": 19.028, "underlyingPrice": 301.54 }
  ]
}
```

:::tip 接口限制
* 30 秒内最多请求 60 次期权标的历史波动率接口（支持分页的接口，仅首次调用纳入统计）
:::

---

# 期权标的排行

`getOptionUnderlyingRank(qotGetOptionUnderlyingRank)`


* **介绍**

    获取期权标的排行列表

* **参数**

```protobuf
message C2S
{
    required int32 optionMarket = 1;    //Qot_OptionCommon.OptionMarket
    required int32 sortType = 2;        //Qot_OptionCommon.UnderlyingRankSortType
    optional bool isAsc = 3;            //是否升序，默认false
    optional int32 count = 4;           //每页数量[1,200]，默认200
    optional string tradingDate = 5;    //交易日，格式yyyy-MM-dd
    repeated Qot_OptionCommon.UnderlyingRankIndicator filterList = 6;
    optional string page = 7;           //分页游标
}

message Request
{
    required C2S c2s = 1;
}
```

* **返回**

```protobuf
message UnderlyingRankItem
{
    required Qot_Common.Security owner = 1;
    optional string name = 2;
    optional int64 totalVolume = 3;
    optional int64 totalOpenInterest = 4;
    optional double volumeRatio = 5;
    optional double openInterestRatio = 6;
    optional double iv = 7;
    optional double ivRank = 8;
    optional double ivPercentile = 9;
    optional double price = 10;
    optional double changeRate = 11;
    optional double ivChange = 12;
    optional double hv = 13;
    optional double hvChange = 14;
    optional double marketCap = 15;
}

message S2C
{
    required int32 optionMarket = 1;
    required int32 sortType = 2;
    optional string tradingDate = 3;
    optional double tradingTimestamp = 4;
    repeated UnderlyingRankItem rankList = 5;
    optional string nextPage = 6;
    optional int32 allCount = 7;
}

message Response
{
    required int32 retType = 1 [default = -400]; //RetType，返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3305

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_OptionCommon } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetOptionUnderlyingRank(){
    const { RetType } = Common
    const { OptionMarket, UnderlyingRankSortType } = Qot_OptionCommon
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11112, false, ''];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: {
                    optionMarket: OptionMarket.OptionMarket_US_Security,
            sortType: UnderlyingRankSortType.UnderlyingRankSortType_Volume,
            count: 5,
                },
            };
            websocket.GetOptionUnderlyingRank(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetOptionUnderlyingRank: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetOptionUnderlyingRank()
```

* **Output**

``` JavaScript
GetOptionUnderlyingRank: errCode 0, retMsg , retType 0
{
  "optionMarket": 1,
  "sortType": 1,
  "tradingDate": "2026-06-12",
  "tradingTimestamp": 1781237000,
  "rankList": [
    {
      "owner": { "market": 1, "code": "SPY" },
      "name": "标普500ETF-SPDR",
      "totalVolume": 14228830,
      "totalOpenInterest": 19909256,
      "volumeRatio": 0.97899,
      "openInterestRatio": 1.93868,
      "iv": 17.675,
      "ivRank": 27.143,
      "ivPercentile": 61.111,
      "price": 741.75,
      "changeRate": 0.540826,
      "ivChange": -8.261,
      "hv": 15.031,
      "hvChange": -0.057,
      "marketCap": 781494500000
    },
    {
      "owner": { "market": 1, "code": "QQQ" },
      "name": "纳指100ETF-Invesco QQQ Trust",
      "totalVolume": 8239190,
      "totalOpenInterest": 12964422,
      "volumeRatio": 0.99417,
      "openInterestRatio": 1.49888,
      "iv": 27.652,
      "ivRank": 62.918,
      "ivPercentile": 91.269,
      "price": 721.34,
      "changeRate": 0.588465,
      "ivChange": -8.332,
      "hv": 26.196,
      "hvChange": -0.644,
      "marketCap": 476553300000
    }
  ],
  "allCount": 6017
}
```

:::tip 接口限制
* 30 秒内最多请求 60 次期权标的排行接口（支持分页的接口，仅首次调用纳入统计）
:::

---

# 期权合约排行

`getOptionRank(qotGetOptionRank)`


* **介绍**

    获取期权合约排行列表

* **参数**

```protobuf
message C2S
{
    required int32 optionMarket = 1; //Qot_OptionCommon.OptionMarket
    required int32 sortType = 2; //Qot_OptionCommon.OptionRankType
    optional int32 count = 3; //返回数量[1,200]，默认200
    optional string tradingDate = 4; //交易日，格式yyyy-MM-dd
    optional bool isAsc = 5; //是否升序，默认false
    optional string page = 6; //分页游标
    repeated Qot_OptionCommon.OptionRankIndicator filterList = 7;
}

message Request
{
    required C2S c2s = 1;
}
```

* **返回**

```protobuf
message OptionRankItem
{
    required Qot_Common.Security option = 1;
    optional string name = 2;
    optional int32 optionType = 3;
    optional int64 oiIncrement = 4;
    optional int64 oiDecrement = 5;
    optional double oiMarketCapIncrement = 6;
    optional double oiMarketCapDecrement = 7;
    optional int64 volume = 8;
    optional double turnover = 9;
    optional int64 openInterest = 10;
    optional double openInterestMarketCap = 11;
    optional double iv = 12;
    optional double optionPrice = 13;
    optional double changeRate = 14;
    optional double midPrice = 15;
    optional double bidPrice = 16;
    optional int64 bidVolume = 17;
    optional double askPrice = 18;
    optional int64 askVolume = 19;
    optional double delta = 20;
    optional double gamma = 21;
    optional double theta = 22;
    optional double vega = 23;
    optional double rho = 24;
}

message S2C
{
    required int32 optionMarket = 1;
    required int32 sortType = 2;
    optional string tradingDate = 3;
    optional double tradingTimestamp = 4;
    repeated OptionRankItem rankList = 5;
    optional string nextPage = 6;
    optional int32 allCount = 7;
}

message Response
{
    required int32 retType = 1 [default = -400]; //RetType，返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3306

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_OptionCommon } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetOptionRank(){
    const { RetType } = Common
    const { OptionMarket, OptionRankType } = Qot_OptionCommon
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11112, false, ''];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: {
                    optionMarket: OptionMarket.OptionMarket_US_Security,
            sortType: OptionRankType.OptionRankType_Volume,
            count: 5,
                },
            };
            websocket.GetOptionRank(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetOptionRank: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetOptionRank()
```

* **Output**

``` JavaScript
GetOptionRank: errCode 0, retMsg , retType 0
{
  "optionMarket": 1,
  "sortType": 1,
  "tradingDate": "2026-06-12",
  "tradingTimestamp": 1781237000,
  "rankList": [
    {
      "option": { "market": 1, "code": "SPY260612C742000" },
      "name": "SPY 260612 742.00C",
      "optionType": 1,
      "oiIncrement": 1816,
      "volume": 730160,
      "turnover": 91928623,
      "openInterest": 7449,
      "iv": 146.507,
      "optionPrice": 0.58,
      "changeRate": -67.688,
      "midPrice": 0.58,
      "bidPrice": 0.56,
      "bidVolume": 28,
      "askPrice": 0.6,
      "askVolume": 1,
      "delta": 0.43674,
      "gamma": 0.27447,
      "theta": -455.46028,
      "vega": 0.00385,
      "rho": 0
    },
    {
      "option": { "market": 1, "code": "SPY260612C745000" },
      "name": "SPY 260612 745.00C",
      "optionType": 1,
      "oiIncrement": 5416,
      "volume": 617981,
      "turnover": 44479304,
      "openInterest": 17013,
      "iv": 87.067,
      "optionPrice": 0.01,
      "changeRate": -98.958,
      "midPrice": 0.015,
      "bidPrice": 0.01,
      "bidVolume": 708,
      "askPrice": 0.02,
      "askVolume": 500,
      "delta": 0.02438,
      "gamma": 0.03501,
      "theta": -18.5231,
      "vega": 0.00107,
      "rho": 0
    }
  ],
  "allCount": 1955829
}
```

:::tip 接口限制
* 30 秒内最多请求 60 次期权合约排行接口（支持分页的接口，仅首次调用纳入统计）
:::

---

# 期权异动

`getOptionEvent(qotGetOptionEvent)`


* **介绍**

    获取期权异动列表

* **参数**

```protobuf
message EventIndicator
{
    required int32 indicatorType = 1;  //Qot_GetOptionEvent.EventIndicatorType
    optional Qot_OptionCommon.IndicatorValue indicatorValue = 2;
}

message EventSort
{
    required int32 indicatorType = 1;  //EventIndicatorType(排序字段)
    required bool isAsc = 2;           //是否升序
}

message C2S
{
    required int32 optionMarket = 1;         //Qot_OptionCommon.OptionMarket
    optional int32 count = 2;                //每页数量[1,300]
    optional string page = 3;                //分页标记，首次为空字符串
    repeated EventIndicator filterList = 4;  //筛选条件列表（条件间AND逻辑）
    optional EventSort sort = 5;             //排序（默认按时间降序）
}

message Request
{
    required C2S c2s = 1;
}
```

* **返回**

```protobuf
message CorporateAction
{
    optional int32 actionType = 1;       //CorporateActionType
    optional string actionTime = 2;      //行动日期("yyyy-MM-dd")
    optional double actionTimestamp = 3;  //行动日期(Unix秒)
}

message EventItem
{
    optional Qot_Common.Security option = 1;  //期权合约标识
    optional Qot_Common.Security owner = 2;   //标的股票标识
    optional string symbol = 3;               //标的display code
    optional string fillTime = 10;            //成交时间
    optional double fillTimestamp = 11;       //成交时间(Unix秒)
    optional int32 tickerType = 12;           //TickerType，成交方向
    optional double price = 13;               //成交价
    optional int64 volume = 14;               //成交量（张）
    optional double turnover = 15;            //成交额
    optional int32 optionType = 20;           //Qot_Common.OptionType
    optional double strikePrice = 21;         //行权价
    optional string strikeTime = 22;          //到期日
    optional double strikeTimestamp = 23;     //到期日(Unix秒)
    optional int32 dte = 24;                  //距到期天数
    optional double underlyingPrice = 30;     //标的价格
    optional double otm = 31;                 //价外比率（百分比）
    optional double bidPrice = 32;            //买一价
    optional double askPrice = 33;            //卖一价
    optional double iv = 34;                  //隐含波动率（百分比）
    optional int64 totalVolume = 35;          //期权当日总成交量
    optional int64 totalOpenInterest = 36;    //期权当日总持仓量
    optional double voRatio = 37;             //量仓比（百分比）
    optional double delta = 40;
    optional double gamma = 41;
    optional double vega = 42;
    optional double theta = 43;
    optional double rho = 44;
    optional int32 sentiment = 50;            //MarketSentiment
    repeated int32 orderTypeList = 51;        //OptionOrderType列表
    optional int32 strategyType = 52;         //TickerStrategy
    optional string earningsTime = 60;        //财报日期
    optional int32 earningsPubType = 61;      //EarningsPubType
    repeated CorporateAction corporateActionList = 63;  //公司行动列表
    repeated Qot_Common.Security industryPlateList = 64;   //行业板块列表
    repeated Qot_Common.Security conceptPlateList = 65;    //概念板块列表
}

message S2C
{
    repeated EventItem eventList = 1;       //异动列表
    optional string nextPage = 2;           //下一页标记（空字符串=无下一页）
    optional int32 allCount = 3;            //总记录数
    optional double updateTimestamp = 4;    //列表更新时间(Unix秒)
}

message Response
{
    required int32 retType = 1 [default = -400]; //RetType，返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3307

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_OptionCommon } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetOptionEvent(){
    const { RetType } = Common
    const { OptionMarket } = Qot_OptionCommon
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11112, false, ''];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: {
                    optionMarket: OptionMarket.OptionMarket_US_Security,
            count: 5,
                },
            };
            websocket.GetOptionEvent(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetOptionEvent: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetOptionEvent()
```

* **Output**

``` JavaScript
GetOptionEvent: errCode 0, retMsg , retType 0
{
  "eventList": [
    {
      "option": { "market": 1, "code": "TLT260618C86000" },
      "owner": { "market": 1, "code": "TLT" },
      "symbol": "TLT",
      "fillTime": "2026-06-12 16:14:00",
      "fillTimestamp": 1781295240,
      "tickerType": 2,
      "price": 0.28,
      "volume": 10000,
      "turnover": 280000,
      "optionType": 1,
      "strikePrice": 86,
      "strikeTime": "2026-06-18",
      "strikeTimestamp": 1781759000,
      "dte": 3,
      "underlyingPrice": 85.77,
      "otm": 0.268,
      "bidPrice": 0.28,
      "askPrice": 0.3,
      "iv": 8.24,
      "totalVolume": 70108,
      "totalOpenInterest": 88849,
      "voRatio": 0.78906,
      "delta": 0.424382,
      "gamma": 0.432194,
      "vega": 0.043077,
      "theta": -0.034441,
      "rho": 0.00594,
      "sentiment": 2,
      "orderTypeList": [2, 1],
      "strategyType": 1
    }
  ],
  "allCount": 164620
}
```

:::tip 接口限制
* 30 秒内最多请求 60 次期权异动接口（支持分页的接口，仅首次调用纳入统计）
:::

---

# 查询异动提醒

`getOptionEventAlert(qotGetOptionEventAlert)`


* **介绍**

    查询已设置的期权异动提醒列表

* **参数**

```protobuf
message C2S {
    optional int32 count = 1;
    optional string page = 2;
}

message Request {
    required C2S c2s = 1;
}
```

* **返回**

```protobuf
message EventAlertItem {
    optional int64 key = 1;
    optional bool enable = 2;
    optional int32 optionMarket = 10;
    optional string watchlistGroupName = 11;
    optional Qot_Common.Security underlying = 12;
    optional int32 optionType = 20;
    repeated int32 sideTypeList = 21;
    repeated int32 orderTypeList = 22;
    optional Qot_OptionCommon.Interval marketCapRange = 30;
    optional Qot_OptionCommon.Interval expiryDaysRange = 31;
    optional Qot_OptionCommon.Interval priceRange = 32;
    optional Qot_OptionCommon.Interval sizeRange = 33;
    optional Qot_OptionCommon.Interval premiumRange = 34;
    optional Qot_OptionCommon.Interval ivRange = 35;
    optional string earningsDateBegin = 41;
    optional string earningsDateEnd = 42;
    optional string note = 50;
}

message S2C {
    repeated EventAlertItem alertList = 1;
    optional string nextPage = 2;
    optional int32 allCount = 3;
}

message Response {
    required int32 retType = 1 [default = -400]; //RetType，返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3308

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common, Qot_OptionCommon } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetOptionEventAlert(){
    const { RetType } = Common
    const { OptionMarket } = Qot_OptionCommon
    const { OptionType } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: {
                    count: 10,
                    page: "",
                },
            };
            websocket.GetOptionEventAlert(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetOptionEventAlert: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetOptionEventAlert()
```

* **Output**

``` JavaScript
GetOptionEventAlert: errCode 0, retMsg , retType 0
{
  "alertList": [
    {
      "key": "1700000000001",
      "enable": true,
      "optionMarket": 0,
      "optionType": 1,
      "orderTypeList": [1],
      "sizeRange": { "filterMin": { "value": 100, "includes": true } },
      "note": "test"
    }
  ],
  "nextPage": "",
  "allCount": 1
}
```

:::tip 接口限制
* 30 秒内最多请求 60 次查询异动提醒接口（支持分页的接口，仅首次调用纳入统计）
:::

---

# 设置异动提醒

`setOptionEventAlert(qotSetOptionEventAlert)`


* **介绍**

    新增、修改、删除或启用/禁用期权异动提醒

* **参数**

```protobuf
enum AlertOpType {
    AlertOpType_Unknown = 0;
    AlertOpType_Add = 1;
    AlertOpType_Delete = 2;
    AlertOpType_Modify = 3;
    AlertOpType_Enable = 4;
    AlertOpType_Disable = 5;
    AlertOpType_DeleteAll = 6;
}

message C2S {
    required int32 operType = 1;
    repeated Qot_GetOptionEventAlert.EventAlertItem alertList = 2;
}

message Request {
    required C2S c2s = 1;
}
```

* **返回**

```protobuf
message S2C {
}

message Response {
    required int32 retType = 1 [default = -400]; //RetType，返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3309

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common, Qot_OptionCommon, Qot_GetOptionEvent, Qot_SetOptionEventAlert } from "futu-api/proto";
import beautify from "js-beautify";

function QotSetOptionEventAlert(){
    const { RetType } = Common
    const { OptionMarket } = Qot_OptionCommon
    const { OptionType } = Qot_Common
    const { OptionOrderType } = Qot_GetOptionEvent
    const { AlertOpType } = Qot_SetOptionEventAlert
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            // 新增一个异动告警：监控美股股票期权市场的 CALL 扫单，成交量 >= 100
            const req = {
                c2s: {
                    operType: AlertOpType.AlertOpType_Add,
                    alertList: [
                        {
                            optionMarket: OptionMarket.OptionMarket_US_Security,
                            optionType: OptionType.OptionType_Call,
                            orderTypeList: [OptionOrderType.OptionOrderType_Sweep],
                            sizeRange: { filterMin: { value: 100, includes: true } },
                            note: "test",
                        }
                    ],
                },
            };
            websocket.SetOptionEventAlert(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("SetOptionEventAlert: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    console.log("新增成功");
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotSetOptionEventAlert()
```

* **Output**

``` JavaScript
SetOptionEventAlert: errCode 0, retMsg , retType 0
新增成功
```

:::tip 接口限制
* 30 秒内最多请求 60 次设置异动提醒接口
:::

---

# 期权异动推送

`onPush_UpdateOptionEvent(qotUpdateOptionEvent)`


* **介绍**

    期权异动推送回调

* **参数**

```protobuf
message S2C
{
    optional Qot_Common.Security owner = 1;         //标的
    optional Qot_Common.Security option = 2;        //期权合约
    optional string message = 3;                    //推送消息文本
}

message Response
{
    required int32 retType = 1 [default = -400]; //RetType，返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3310

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotUpdateOptionEvent(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11112, false, ''];
    let websocket = new ftWebsocket();

    // 需要已通过 SetOptionEventAlert 设置期权异动提醒，推送才会触发
    websocket.onPush = (cmd, res)=>{
        if(ftCmdID.QotUpdateOptionEvent.cmd == cmd){
            let { retType, s2c } = res
            if(retType == RetType.RetType_Succeed){
                let data = beautify(JSON.stringify(s2c), {
                    indent_size: 2,
                    space_in_empty_paren: true,
                });
                console.log("UpdateOptionEvent:");
                console.log(data);
            } else {
                console.log("UpdateOptionEvent: error")
            }
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{
        websocket.stop();
        console.log("stop");
    }, 3600 * 1000);
}

QotUpdateOptionEvent()
```

* **Output**

``` JavaScript
UpdateOptionEvent:
{
  "owner": { "market": 1, "code": "TSLA" },
  "option": { "market": 1, "code": "TSLA250620C250" },
  "message": "TSLA $250 Call 06/20 大额扫单 500张 成交价$12.50"
}
stop
```

---

# 末日期权标的筛选

`getOptionZeroDteScreener(qotGetOptionZeroDteScreener)`


* **介绍**

    获取末日期权标的筛选列表

* **参数**

```protobuf
message C2S {
    required int32 optionMarket = 1;
    optional int32 sortType = 2;   //ZeroDteSortType
    optional bool isAsc = 3;
    optional int32 count = 4;      //[1,500]，默认50
    optional string page = 5;
    repeated Qot_OptionCommon.ZeroDteIndicator filterList = 6;
}

message Request
{
    required C2S c2s = 1;
}
```

* **返回**

```protobuf
message OptionChainInfo {
    optional int64 strikeDateTimestamp = 1;
    optional string productCode = 2;
    optional double multiplier = 3;
    optional double contractShareSize = 4;
    optional int32 expirationType = 5;
    optional Qot_Common.Security underlying = 6;
}

message ZeroDteScreenerItem {
    required Qot_Common.Security owner = 1;
    optional string name = 2;
    optional double price = 3;
    optional double changeRate = 4;
    optional double marketCap = 5;
    optional double iv = 6;
    optional double ivRank = 7;
    optional double ivPercentile = 8;
    optional double hv = 9;
    optional int64 volume = 10;
    optional int64 openInterest = 11;
    optional int64 lastTradingTime = 12;
    optional int64 earningsTimestamp = 13;
    optional string earningsTime = 14;
    optional int32 earningsPubType = 15;
    optional OptionChainInfo chainInfo = 16;
}

message S2C {
    repeated ZeroDteScreenerItem itemList = 1;
    optional string nextPage = 2;
    optional double updateTimestamp = 3;
}

message Response
{
    required int32 retType = 1 [default = -400]; //RetType，返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3311

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_OptionCommon } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetOptionZeroDteScreener(){
    const { RetType } = Common
    const { OptionMarket, ZeroDteSortType } = Qot_OptionCommon
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11112, false, ''];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: {
                    optionMarket: OptionMarket.OptionMarket_US_Security,
            sortType: ZeroDteSortType.ZeroDteSortType_Volume,
            count: 5,
                },
            };
            websocket.GetOptionZeroDteScreener(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetOptionZeroDteScreener: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetOptionZeroDteScreener()
```

* **Output**

``` JavaScript
GetOptionZeroDteScreener: errCode 0, retMsg , retType 0
{
  "itemList": [
    {
      "owner": { "market": 1, "code": "SPY" },
      "name": "标普500ETF-SPDR",
      "price": 741.75,
      "changeRate": 0.54,
      "marketCap": 783071700000,
      "iv": 17.675,
      "ivRank": 27.143,
      "ivPercentile": 61.111,
      "hv": 15.031,
      "volume": 14228830,
      "openInterest": 19909256,
      "lastTradingTime": 1781554500,
      "chainInfo": {
        "strikeDateTimestamp": 1781499600,
        "productCode": "SPY",
        "multiplier": 100,
        "contractShareSize": 100
      }
    },
    {
      "owner": { "market": 1, "code": "QQQ" },
      "name": "纳指100ETF-Invesco QQQ Trust",
      "price": 721.34,
      "changeRate": 0.588,
      "marketCap": 480534900000,
      "iv": 27.652,
      "ivRank": 62.918,
      "ivPercentile": 91.269,
      "hv": 26.196,
      "volume": 8239190,
      "openInterest": 12964422,
      "lastTradingTime": 1781554500,
      "chainInfo": {
        "strikeDateTimestamp": 1781499600,
        "productCode": "QQQ",
        "multiplier": 100,
        "contractShareSize": 100
      }
    }
  ],
  "updateTimestamp": 1781554500
}
```

:::tip 接口限制
* 30 秒内最多请求 60 次末日期权标的筛选接口（支持分页的接口，仅首次调用纳入统计）
:::

---

# 末日期权合约列表

`getOptionZeroDteContract(qotGetOptionZeroDteContract)`


* **介绍**

    获取末日期权合约列表

* **参数**

```protobuf
message C2S {
    required Qot_Common.Security owner = 1;
    required int64 strikeDateTimestamp = 2;
    required Qot_GetOptionZeroDteScreener.OptionChainInfo chainInfo = 3;
    optional int32 sortType = 4;              // Qot_OptionCommon.ZeroDteContractSortType
    optional bool isAsc = 5;                  // 默认 false
    repeated Qot_OptionCommon.ZeroDteContractIndicator filterList = 6;
}

message Request {
    required C2S c2s = 1;
}
```

* **返回**

```protobuf
message ZeroDteContractItem {
    required Qot_Common.Security option = 1;
    optional string name = 2;
    optional int32 optionType = 3;             // Qot_Common.OptionType
    optional double optionPrice = 4;
    optional double changeRate = 5;            // 涨跌幅（百分比）
    optional int64 volume = 6;
    optional int64 openInterest = 7;
    optional double iv = 8;                    // (%)
    optional double delta = 9;
    optional double gamma = 10;
    optional double vega = 11;
    optional double theta = 12;
    optional double rho = 13;
    optional double buyBreakEvenPoint = 14;    // 价格
    optional double buyToBep = 15;             // (%)
    optional double buyProfitProbability = 16; // (%)
    optional double sellProfitProbability = 17;// (%)
}

message S2C {
    repeated ZeroDteContractItem itemList = 1;
}

message Response {
    required int32 retType = 1 [default = -400];
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3312

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_OptionCommon } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetOptionZeroDteContract(){
    const { RetType } = Common
    const { OptionMarket, ZeroDteSortType, ZeroDteContractSortType } = Qot_OptionCommon
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11112, false, ''];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            // 第一步：获取末日期权标的列表，取第一条的 chainInfo
            websocket.GetOptionZeroDteScreener({
                c2s: {
                    optionMarket: OptionMarket.OptionMarket_US_Security,
                    sortType: ZeroDteSortType.ZeroDteSortType_Volume,
                    count: 1,
                },
            })
            .then((screenerRes)=>{
                let { s2c: screenerS2c } = screenerRes
                if (!screenerS2c || !screenerS2c.itemList || screenerS2c.itemList.length === 0) return
                let { owner, chainInfo } = screenerS2c.itemList[0]
                // 第二步：用 chainInfo 查询末日期权合约列表
                return websocket.GetOptionZeroDteContract({
                    c2s: {
                        owner: owner,
                        strikeDateTimestamp: chainInfo.strikeDateTimestamp,
                        chainInfo: chainInfo,
                        sortType: ZeroDteContractSortType.ZeroDteContractSortType_Volume,
                    },
                })
            })
            .then((res)=>{
                if (!res) return
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetOptionZeroDteContract: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetOptionZeroDteContract()
```

* **Output**

``` JavaScript
GetOptionZeroDteContract: errCode 0, retMsg , retType 0
{
  "itemList": [
    {
      "option": { "market": 1, "code": "SPY260612C742000" },
      "name": "SPY 260612 C742",
      "optionType": 1,
      "optionPrice": 0.58,
      "changeRate": -67.688,
      "volume": 730160,
      "openInterest": 7449,
      "iv": 146.5,
      "delta": 0.4367,
      "gamma": 0.2745,
      "vega": 0.0039,
      "theta": -455.46,
      "rho": 0,
      "buyBreakEvenPoint": 742.58,
      "buyToBep": 0.11,
      "buyProfitProbability": 43.5,
      "sellProfitProbability": 56.5
    },
    {
      "option": { "market": 1, "code": "SPY260612C745000" },
      "name": "SPY 260612 C745",
      "optionType": 1,
      "optionPrice": 0.01,
      "changeRate": -98.958,
      "volume": 617981,
      "openInterest": 17013,
      "iv": 87.1,
      "delta": 0.0244,
      "gamma": 0.035,
      "vega": 0.0011,
      "theta": -18.52,
      "rho": 0,
      "buyBreakEvenPoint": 745.01,
      "buyToBep": 0.44,
      "buyProfitProbability": 2.4,
      "sellProfitProbability": 97.6
    }
  ]
}
```

:::tip 接口限制
* 30 秒内最多请求 60 次末日期权合约列表接口
:::

---

# 财报期权筛选

`getOptionEarningsScreener(qotGetOptionEarningsScreener)`


* **介绍**

    获取即将发布财报的期权标的列表

* **参数**

```protobuf
message C2S {
    required int32 optionMarket = 1;      // Qot_OptionCommon.OptionMarket
    optional int32 sortType = 2;          // Qot_OptionCommon.EarningsSortType
    optional bool isAsc = 3;              // 默认 true
    optional int32 count = 4;             // [1,500]（默认50）
    optional string page = 5;
    repeated Qot_OptionCommon.EarningsIndicator filterList = 6;
}

message Request
{
    required C2S c2s = 1;
}
```

* **返回**

```protobuf
message EarningsItem {
    required Qot_Common.Security owner = 1;
    optional string name = 2;
    optional double price = 3;
    optional double changeRate = 4;
    optional double marketCap = 5;
    optional double iv = 6;                        // (%)
    optional double ivRank = 7;                    // (%)
    optional double ivPercentile = 8;              // (%)
    optional double hv = 9;                        // (%)
    optional int64 volume = 10;
    optional int64 openInterest = 11;
    optional double earningsTimestamp = 12;
    optional string earningsTime = 13;
    optional int32 earningsPubType = 14;           // Qot_OptionCommon.EarningsPubType
    optional string earningsQuarter = 15;
    optional double lastReportIvCrush = 16;        // (%)
    optional double historyReportIvCrush = 17;     // (%)
    optional double lastReportChgRate = 18;
    optional double historyReportChgRate = 19;
    optional double estimateEpsYoy = 20;           // (%)
    optional double estimateRevenueYoy = 21;       // (%)
    optional double expectedMoveRatio = 22;        // (%)
}

message S2C {
    repeated EarningsItem itemList = 1;
    optional string nextPage = 2;
    optional double updateTimestamp = 3;
    optional int32 allCount = 4;
}

message Response
{
    required int32 retType = 1 [default = -400]; //RetType，返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3313

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_OptionCommon } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetOptionEarningsScreener(){
    const { RetType } = Common
    const { OptionMarket } = Qot_OptionCommon
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11112, false, ''];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: {
                    optionMarket: OptionMarket.OptionMarket_US_Security,
            count: 5,
                },
            };
            websocket.GetOptionEarningsScreener(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetOptionEarningsScreener: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetOptionEarningsScreener()
```

* **Output**

``` JavaScript
GetOptionEarningsScreener: errCode 0, retMsg , retType 0
{
  "itemList": [
    {
      "owner": { "market": 1, "code": "CGC" },
      "name": "Canopy Growth",
      "price": 1,
      "changeRate": -0.99,
      "marketCap": 422019000,
      "iv": 204.207,
      "ivRank": 36.55,
      "ivPercentile": 88.492,
      "hv": 39.545,
      "volume": 8131,
      "openInterest": 328382,
      "earningsTimestamp": 1781496000,
      "earningsTime": "2026-06-15",
      "earningsPubType": 1,
      "earningsQuarter": "2026Q4",
      "lastReportIvCrush": -21.308,
      "historyReportIvCrush": 11.782,
      "lastReportChgRate": 1.851,
      "historyReportChgRate": 12.761,
      "estimateEpsYoy": 94.055,
      "estimateRevenueYoy": 14.34,
      "expectedMoveRatio": 12.5
    },
    {
      "owner": { "market": 1, "code": "PLAY" },
      "name": "Dave & Buster's Entertainment",
      "price": 12.93,
      "changeRate": -1.896,
      "marketCap": 449180500,
      "iv": 114.03,
      "ivRank": 99.492,
      "ivPercentile": 99.603,
      "hv": 62.39,
      "volume": 3052,
      "openInterest": 44247,
      "earningsTimestamp": 1781496000,
      "earningsTime": "2026-06-15",
      "earningsPubType": 2,
      "earningsQuarter": "2027Q1",
      "lastReportIvCrush": 22.64,
      "historyReportIvCrush": 26.059,
      "lastReportChgRate": 16.066,
      "historyReportChgRate": 15.892,
      "estimateEpsYoy": -3.758,
      "estimateRevenueYoy": 1.881,
      "expectedMoveRatio": 15.409
    }
  ],
  "allCount": 292
}
```

:::tip 接口限制
* 30 秒内最多请求 60 次财报期权筛选接口（支持分页的接口，仅首次调用纳入统计）
:::

---

# 期权卖方专区

`getOptionSellerScreener(qotGetOptionSellerScreener)`


* **介绍**

    获取期权卖方专区筛选列表

* **参数**

```protobuf
message C2S {
    required int32 optionMarket = 1;      // Qot_OptionCommon.OptionMarket
    required int32 sellerType = 2;        // Qot_OptionCommon.SellerType
    optional int32 sortType = 3;          // Qot_OptionCommon.SellerSortType
    optional bool isAsc = 4;              // 默认 false
    repeated Qot_OptionCommon.SellerIndicator filterList = 5;
}

message Request {
    required C2S c2s = 1;
}
```

* **返回**

```protobuf
message SellerItem {
    required Qot_Common.Security option = 1;
    optional string name = 2;
    optional int32 optionType = 3;                  // Qot_Common.OptionType
    optional double strikePrice = 4;
    optional string strikeTime = 5;
    optional double strikeTimestamp = 6;
    optional int32 leftDays = 7;
    optional double optionPrice = 8;
    optional double stockPrice = 9;
    optional double premium = 10;
    optional double otmDegree = 11;                 // (%)
    optional double iv = 12;                        // (%)
    optional double intervalReturn = 13;            // (%)
    optional double annualizedReturn = 14;          // (%)
    optional double itmProbability = 15;            // (%)
    optional double strikedIntervalReturn = 16;     // (%)
    optional double strikedAnnualizedReturn = 17;   // (%)
    optional Qot_Common.Security owner = 18;
}

message S2C {
    repeated SellerItem itemList = 1;
}

message Response {
    required int32 retType = 1 [default = -400];
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3314

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_OptionCommon } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetOptionSellerScreener(){
    const { RetType } = Common
    const { OptionMarket, SellerType, SellerSortType } = Qot_OptionCommon
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11112, false, ''];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: {
                    optionMarket: OptionMarket.OptionMarket_US_Security,
            sellerType: SellerType.SellerType_CoveredCall,
            sortType: SellerSortType.SellerSortType_AnnualizedReturn,
                },
            };
            websocket.GetOptionSellerScreener(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetOptionSellerScreener: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetOptionSellerScreener()
```

* **Output**

``` JavaScript
GetOptionSellerScreener: errCode 0, retMsg , retType 0
{
  "itemList": [
    {
      "option": { "market": 1, "code": "SOXL260618C235000" },
      "name": "SOXL 260618 235.00C",
      "optionType": 1,
      "strikePrice": 235,
      "strikeTime": "2026-06-18",
      "strikeTimestamp": 1781755000,
      "leftDays": 3,
      "optionPrice": 21.85,
      "stockPrice": 234.68,
      "premium": 2185,
      "otmDegree": 0.136,
      "iv": 234.988,
      "intervalReturn": 10.266,
      "annualizedReturn": 1074.855,
      "itmProbability": 45.724,
      "strikedIntervalReturn": 10.416,
      "strikedAnnualizedReturn": 1090.597,
      "owner": { "market": 1, "code": "SOXL" }
    },
    {
      "option": { "market": 1, "code": "SOXL260618C237500" },
      "name": "SOXL 260618 237.50C",
      "optionType": 1,
      "strikePrice": 237.5,
      "strikeTime": "2026-06-18",
      "strikeTimestamp": 1781755000,
      "leftDays": 3,
      "optionPrice": 20.675,
      "stockPrice": 234.68,
      "premium": 2067.5,
      "otmDegree": 1.201,
      "iv": 234.423,
      "intervalReturn": 9.66,
      "annualizedReturn": 1011.47,
      "itmProbability": 43.682,
      "strikedIntervalReturn": 10.978,
      "strikedAnnualizedReturn": 1149.431,
      "owner": { "market": 1, "code": "SOXL" }
    }
  ]
}
```

:::tip 接口限制
* 30 秒内最多请求 60 次期权卖方专区接口
:::

---

# 筛选窝轮

`GetWarrant(req);`

* **介绍**

    筛选窝轮（仅用于香港市场）

* **参数**

```protobuf
message C2S
{
	required int32 begin = 1; //数据起始点
	required int32 num =  2; //请求数据个数，最大200
	required int32 sortField = 3;//Qot_Common.SortField，根据哪个字段排序
	required bool ascend = 4;//升序 ture，降序 false
	
	//以下为筛选条件，可选字段，不填表示不过滤
	optional Qot_Common.Security owner = 5;	//所属正股
	repeated int32 typeList = 6; //Qot_Common.WarrantType，窝轮类型过滤列表
	repeated int32 issuerList = 7; //Qot_Common.Issuer，发行人过滤列表
	optional string maturityTimeMin = 8; //到期日，到期日范围的开始时间戳
	optional string maturityTimeMax = 9; //到期日范围的结束时间戳
	optional int32 ipoPeriod = 10; //Qot_Common.IpoPeriod，上市日
	optional int32 priceType = 11; //Qot_Common.PriceType，价内/价外（暂不支持界内证的界内外筛选）
	optional int32 status = 12; //Qot_Common.WarrantStatus，窝轮状态
	optional double curPriceMin = 13; //最新价的过滤下限（闭区间），不传代表下限为 -∞（精确到小数点后 3 位，超出部分会被舍弃）
	optional double curPriceMax = 14; //最新价的过滤上限（闭区间），不传代表上限为 +∞（精确到小数点后 3 位，超出部分会被舍弃） 	
	optional double strikePriceMin = 15; //行使价的过滤下限（闭区间），不传代表下限为 -∞（精确到小数点后 3 位，超出部分会被舍弃）
	optional double strikePriceMax = 16; //行使价的过滤上限（闭区间），不传代表上限为 +∞（精确到小数点后 3 位，超出部分会被舍弃） 
	optional double streetMin = 17; //街货占比的过滤下限（闭区间），该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。不传代表下限为 -∞（精确到小数点后 3 位，超出部分会被舍弃）
	optional double streetMax = 18; //街货占比的过滤上限（闭区间），该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。不传代表上限为 +∞（精确到小数点后 3 位，超出部分会被舍弃）
	optional double conversionMin = 19; //换股比率的过滤下限（闭区间），不传代表下限为 -∞（精确到小数点后 3 位，超出部分会被舍弃）
	optional double conversionMax = 20; //换股比率的过滤上限（闭区间），不传代表上限为 +∞（精确到小数点后 3 位，超出部分会被舍弃）
	optional uint64 volMin = 21; //成交量的过滤下限（闭区间），不传代表下限为 -∞
	optional uint64 volMax = 22; //成交量的过滤上限（闭区间），不传代表上限为 +∞
	optional double premiumMin = 23; //溢价的过滤下限（闭区间），该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。不传代表下限为 -∞（精确到小数点后 3 位，超出部分会被舍弃）
	optional double premiumMax = 24; //溢价的过滤上限（闭区间），该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。不传代表上限为 +∞（精确到小数点后 3 位，超出部分会被舍弃）
	optional double leverageRatioMin = 25; //杠杆比率的过滤下限（闭区间），不传代表下限为 -∞（精确到小数点后 3 位，超出部分会被舍弃）
	optional double leverageRatioMax = 26; //杠杆比率的过滤上限（闭区间），不传代表上限为 +∞（精确到小数点后 3 位，超出部分会被舍弃）
	optional double deltaMin = 27;//对冲值的过滤下限（闭区间），仅认购认沽支持此字段过滤，不传代表下限为 -∞（精确到小数点后 3 位，超出部分会被舍弃）
	optional double deltaMax = 28;//对冲值的过滤上限（闭区间），仅认购认沽支持此字段过滤，不传代表上限为 +∞（精确到小数点后 3 位，超出部分会被舍弃）
	optional double impliedMin = 29; //引伸波幅的过滤下限（闭区间），仅认购认沽支持此字段过滤，不传代表下限为 -∞（精确到小数点后 3 位，超出部分会被舍弃）
	optional double impliedMax = 30; //引伸波幅的过滤上限（闭区间），仅认购认沽支持此字段过滤，不传代表上限为 +∞（精确到小数点后 3 位，超出部分会被舍弃）	
	optional double recoveryPriceMin = 31; //收回价的过滤下限（闭区间），仅牛熊证支持此字段过滤，不传代表下限为 -∞（精确到小数点后 3 位，超出部分会被舍弃）
	optional double recoveryPriceMax = 32; //收回价的过滤上限（闭区间），仅牛熊证支持此字段过滤，不传代表上限为 +∞（精确到小数点后 3 位，超出部分会被舍弃）
	optional double priceRecoveryRatioMin = 33;//正股距收回价，的过滤下限（闭区间），仅牛熊证支持此字段过滤。该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。不传代表下限为 -∞（精确到小数点后 3 位，超出部分会被舍弃）
	optional double priceRecoveryRatioMax = 34;//正股距收回价，的过滤上限（闭区间），仅牛熊证支持此字段过滤。该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。不传代表上限为 +∞（精确到小数点后 3 位，超出部分会被舍弃）	
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 排序类型参见 [SortField](./quote.md#2930)
>    - 窝轮类型过滤列表参见 [WarrantType](./quote.md#926)
>    - 发行人过滤列表参见 [Issuer](./quote.md#8363)
>    - 上市日类型参见 [IpoPeriod](./quote.md#9546)
>    - 价内价外类型参见 [PriceType](./quote.md#6407)
>    - 窝轮状态类型参见 [WarrantStatus](./quote.md#6556)

* **返回**

```protobuf
message WarrantData
{
	//静态数据项
    required Qot_Common.Security stock = 1; //股票
    required Qot_Common.Security owner = 2; //所属正股
	required int32 type = 3; //Qot_Common.WarrantType，窝轮类型
    required int32 issuer = 4; //Qot_Common.Issuer，发行人
	required string maturityTime = 5; //到期日
	optional double maturityTimestamp = 6; //到期日时间戳
	required string listTime = 7; //上市时间（格式：yyyy-MM-dd）
	optional double listTimestamp = 8; //上市时间戳
	required string lastTradeTime = 9; //最后交易日
	optional double lastTradeTimestamp = 10; //最后交易日时间戳
	optional double recoveryPrice = 11; //收回价，仅牛熊证支持此字段
	required double conversionRatio = 12; //换股比率
	required int32 lotSize = 13; //每手数量
	required double strikePrice = 14; //行使价	
	required double lastClosePrice = 15; //昨收价        
	required string name = 16; //名称	

	//动态数据项
	required double curPrice = 17; //当前价
	required double priceChangeVal = 18; //涨跌额
    required double changeRate = 19; //涨跌幅（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）	
	required int32 status = 20; //Qot_Common.WarrantStatus，窝轮状态	
    required double bidPrice = 21; //买入价	
	required double askPrice = 22; //卖出价
    required int64 bidVol = 23; //买量
	required int64 askVol = 24; //卖量
	required int64 volume = 25; //成交量
    required double turnover = 26; //成交额	
	required double score = 27; //综合评分
	required double premium = 28; //溢价（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
    required double breakEvenPoint = 29; //打和点	
    required double leverage = 30; //杠杆比率（倍）
    required double ipop = 31; //价内/价外，正数表示价内，负数表示价外（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）        	
	optional double priceRecoveryRatio = 32; //正股距收回价，仅牛熊证支持此字段（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
	required double conversionPrice = 33; //换股价
	required double streetRate = 34; //街货占比（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）	
	required int64 streetVol = 35; //街货量
	required double amplitude = 36; //振幅（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
	required int64 issueSize = 37; //发行量	        
	required double highPrice = 39; //最高价
    required double lowPrice = 40; //最低价	
	optional double impliedVolatility = 41; //引申波幅，仅认购认沽支持此字段
    optional double delta = 42; //对冲值，仅认购认沽支持此字段
	required double effectiveLeverage = 43; //有效杠杆
	optional double upperStrikePrice = 44; //上限价，仅界内证支持此字段
	optional double lowerStrikePrice = 45; //下限价，仅界内证支持此字段
	optional int32 inLinePriceStatus = 46; //Qot_Common.PriceType，界内界外，仅界内证支持此字段
}

message S2C
{
    required bool lastPage = 1; //是否最后一页了，false:非最后一页，还有窝轮记录未返回; true:已是最后一页
	required int32 allCount = 2; //该条件请求所有数据的个数
    repeated WarrantData warrantDataList = 3; //窝轮数据
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType，返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	optional S2C s2c = 4;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 窝轮类型过滤列表参见 [WarrantType](./quote.md#926)
>    - 发行人过滤列表参见 [Issuer](./quote.md#8363)
>    - 价内价外类型参见 [PriceType](./quote.md#6407)
>    - 窝轮状态类型参见 [WarrantStatus](./quote.md#6556)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetWarrant(){
    const { RetType } = Common
    const { SortField, QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功

            const req = {
                c2s: {
                    begin: 0,
                    num: 2,
                    sortField: SortField.SortField_CurPrice,
                    ascend: true,

                    owner:{
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                },
            };

            websocket.GetWarrant(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("Warrant: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
Warrant: errCode 0, retMsg , retType 0
{
  "lastPage": false,
  "allCount": 1401,
  "warrantDataList": [{
    "stock": {
      "market": 1,
      "code": "50710"
    },
    "owner": {
      "market": 1,
      "code": "00700"
    },
    "type": 3,
    "issuer": 7,
    "maturityTime": "2022-04-14",
    "maturityTimestamp": 1649865600,
    "listTime": "2021-09-10",
    "listTimestamp": 1631203200,
    "lastTradeTime": "2022-04-13",
    "lastTradeTimestamp": 1649779200,
    "recoveryPrice": 502.88,
    "conversionRatio": 500,
    "lotSize": 50000,
    "strikePrice": 498.88,
    "lastClosePrice": 0,
    "name": "腾讯汇丰二四牛C.C",
    "curPrice": 0,
    "priceChangeVal": 0,
    "changeRate": 0,
    "status": 3,
    "bidPrice": 0,
    "askPrice": 0,
    "bidVol": "0",
    "askVol": "0",
    "volume": "0",
    "turnover": 0,
    "score": 0.199,
    "premium": 2.819,
    "breakEvenPoint": 498.88,
    "leverage": 0,
    "ipop": -2.742,
    "priceRecoveryRatio": -3.5157492841234506,
    "conversionPrice": 0,
    "streetRate": 0,
    "streetVol": "0",
    "amplitude": 0,
    "issueSize": "100000000",
    "highPrice": 0,
    "lowPrice": 0,
    "effectiveLeverage": 0
  }, {
    "stock": {
      "market": 1,
      "code": "50833"
    },
    "owner": {
      "market": 1,
      "code": "00700"
    },
    "type": 3,
    "issuer": 11,
    "maturityTime": "2022-01-28",
    "maturityTimestamp": 1643299200,
    "listTime": "2021-09-10",
    "listTimestamp": 1631203200,
    "lastTradeTime": "2022-01-27",
    "lastTradeTimestamp": 1643212800,
    "recoveryPrice": 518,
    "conversionRatio": 100,
    "lotSize": 10000,
    "strikePrice": 515,
    "lastClosePrice": 0,
    "name": "腾讯瑞银二一牛C.C",
    "curPrice": 0,
    "priceChangeVal": 0,
    "changeRate": 0,
    "status": 3,
    "bidPrice": 0,
    "askPrice": 0,
    "bidVol": "0",
    "askVol": "0",
    "volume": "0",
    "turnover": 0,
    "score": 0.196,
    "premium": 6.141,
    "breakEvenPoint": 515,
    "leverage": 0,
    "ipop": -5.786,
    "priceRecoveryRatio": -6.3320463320463345,
    "conversionPrice": 0,
    "streetRate": 0,
    "streetVol": "0",
    "amplitude": 0,
    "issueSize": "40000000",
    "highPrice": 0,
    "lowPrice": 0,
    "effectiveLeverage": 0
  }]
}
stop
```

:::tip 接口限制
* 港股 BMP 权限不支持调用此接口
* 每 30 秒内最多请求 60 次筛选窝轮接口
* 每次请求的数据个数上限为 200 个
:::

---

# 筛选窝轮 V2

`GetWarrantScreen(req);`


* **介绍**

    窝轮筛选 V2

* **参数**

```protobuf
message Boundary
{
    required double value = 1;
    optional bool includes = 2;     // 是否闭区间，默认 true
}

message Interval
{
    optional Boundary filterMin = 1;
    optional Boundary filterMax = 2;
}

message Choice
{
    required int32 contentType = 1; // 1=数值, 2=文本
    optional string text = 2;
    optional int64 value = 3;
}

// 一条筛选条件：interval / choices 二选一
message ScreenGroup
{
    required int32 fieldId = 1;     // WarrantField 枚举
    optional Interval interval = 2; // 区间筛选
    repeated Choice choices = 3;    // 多选筛选
}

message Sort
{
    required int32 sortFieldId = 1;
    required int32 direction = 2;   // 0=升序, 1=降序
}

message C2S
{
    required int32 marketType = 1;          // 市场，HK=1、SG=4、MY=15
    optional bool isDelay = 2;
    repeated ScreenGroup filterList = 3;
    repeated Sort sortList = 4;
    optional bool onlyCount = 5;            // 仅返回总数
    optional int32 pageFrom = 6;
    optional int32 pageCount = 7;
}

message Request
{
    required C2S c2s = 1;
}
```

* **返回**

```protobuf
message WarrantItem
{
    optional int64 stockId = 1;
    optional int64 stockOwner = 2;
    optional int32 issuerId = 3;
    optional int32 warrantType = 4;     // 1=认购,2=认沽,3=牛证,4=熊证,5=界内证
    optional double strikePrice = 5;
    optional string maturityDate = 6;
    optional string lastTradeDate = 7;
    optional double conversionRatio = 8;
    optional double lastclosePrice = 9;
    optional double recoveryPrice = 10;
    optional double stockOwnerPrice = 11;
    optional double currentPrice = 12;
    optional int64 volume = 13;
    optional double turnover = 14;
    optional int64 sellVol = 15;
    optional int64 buyVol = 16;
    optional double sellPrice = 17;
    optional double buyPrice = 18;
    optional double streetRate = 19;
    optional double highPrice = 20;
    optional double lowPrice = 21;
    optional double impliedVolatility = 22;
    optional double delta = 23;
    optional int32 status = 24;
    optional double streetRateNew = 25;
    optional double score = 26;
    optional double premium = 27;
    optional double leverage = 28;
    optional double effectiveLeverage = 29;
    optional double breakEvenPoint = 30;
    optional double ipop = 31;
    optional double amplitude = 32;
    optional double fxScore = 33;
    optional string ipoTime = 34;
    optional int64 streetVol = 35;
    optional int32 lotSize = 36;
    optional int64 issueSize = 37;
    optional double ipoPrice = 38;
    optional double upperStrikePrice = 39;
    optional double lowerStrikePrice = 40;
    optional int32 iwPriceStatus = 41;
    optional double sensitivity = 42;
    optional double priceRecoveryRatio = 43;
    optional string code = 44;          // 窝轮代码，带 market 前缀（如 HK.10001），OpenD 反查填充
    optional string ownerCode = 45;     // 正股代码，带 market 前缀（如 HK.00700）
    optional string name = 46;          // 窝轮名称
    optional string ownerName = 47;     // 正股名称
}

message S2C
{
    required bool lastPage = 1;
    required int32 allCount = 2;
    repeated WarrantItem warrants = 3;
}

message Response
{
    required int32 retType = 1 [default = -400];
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3254

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetWarrantScreen(){
    const { RetType } = Common
    // FieldId 为数值常量: 1=代码, 4=发行人, 5=正股, 6=类型, 8=最新价；WarrantType: 1=认购, 2=认沽
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            // 筛选腾讯正股的认购证，按最新价降序取回前 5 条
            const req = {
                c2s: {
                    marketType: 1,
                    filterList: [
                        { fieldId: 5, choices: [{ contentType: 1, value: 54047868453564 }] },
                        { fieldId: 6, choices: [{ contentType: 1, value: 1 /* WarrantType.Call 认购 */ }] }
                    ],
                    sortList: [
                        { sortFieldId: 8 /* FieldId 最新价 */, direction: 1 }
                    ],
                    pageFrom: 0,
                    pageCount: 5,
                },
            };
            websocket.GetWarrantScreen(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetWarrantScreen: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetWarrantScreen()
```

* **Output**

``` JavaScript
GetWarrantScreen: errCode 0, retMsg , retType 0
{
  "warrants": [
    {
      "stockId": "91190000000001",
      "stockOwner": "54047868453564",
      "issuerId": 1001,
      "warrantType": 1,
      "strikePrice": 600.0,
      "maturityDate": "1778025600",
      "lastTradeDate": "1777939200",
      "conversionRatio": 100,
      "lastclosePrice": 0.85,
      "stockOwnerPrice": 460.0,
      "currentPrice": 1.05,
      "volume": 1200000,
      "turnover": 1260000,
      "sellVol": 50000,
      "buyVol": 80000,
      "sellPrice": 1.06,
      "buyPrice": 1.04,
      "streetRate": 25.5,
      "highPrice": 1.08,
      "lowPrice": 1.02,
      "impliedVolatility": 32.5,
      "delta": 0.55,
      "status": 0,
      "streetRateNew": 25.5,
      "score": 8.5,
      "premium": 30.43,
      "leverage": 5.24,
      "effectiveLeverage": 2.88,
      "breakEvenPoint": 585.0,
      "ipop": 30.43,
      "amplitude": 5.88,
      "fxScore": 8.0,
      "streetVol": 3000000,
      "lotSize": 10000,
      "issueSize": 500000000,
      "ipoPrice": 0.5,
      "sensitivity": 2.88,
      "priceRecoveryRatio": 23.33,
      "security": { "market": 2, "code": "10001" },
      "ownerSecurity": { "market": 2, "code": "00700" },
      "name": "腾讯法兴五八A",
      "ownerName": "腾讯控股"
    }
  ],
  "lastPage": true,
  "allCount": 1
}
```

:::tip 接口限制
* 每 30 秒内最多请求 60 次筛选窝轮接口
:::

---

# 获取窝轮和期货列表

`GetReference(req);`

* **介绍**

    获取证券的关联数据，如：获取正股相关窝轮、获取期货相关合约

* **参数**

```protobuf
enum ReferenceType
{
	ReferenceType_Unknow = 0; 
	ReferenceType_Warrant = 1; //正股相关的窝轮
	ReferenceType_Future = 2; //期货主连的相关合约
}

message C2S
{
	required Qot_Common.Security security = 1; //股票
	required int32 referenceType = 2; // ReferenceType，相关类型
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)

* **返回**

```protobuf
message S2C
{
	repeated Qot_Common.SecurityStaticInfo staticInfoList = 2; //相关股票列表
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType，返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 股票静态信息结构参见 [SecurityStaticInfo](./quote.md#609)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common, Qot_GetReference } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetReference(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    const { ReferenceType } = Qot_GetReference
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功

            const req = {
                c2s: {
                    security:{
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                    referenceType: ReferenceType.ReferenceType_Warrant,
                },
            };

            websocket.GetReference(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("Reference: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
Reference: errCode 0, retMsg , retType 0
{
  "staticInfoList": [{
    "basic": {
      "security": {
        "market": 1,
        "code": "24719"
      },
      "id": "76128295346319",
      "lotSize": 1000,
      "secType": 5,
      "name": "腾讯东亚九四沽A",
      "listTime": "2018-07-20",
      "delisting": false,
      "listTimestamp": 1532016000
    },
    "warrantExData": {
      "type": 2,
      "owner": {
        "market": 1,
        "code": "00700"
      }
    }
  }, {
    "basic": {
      "security": {
        "market": 1,
        "code": "27227"
      },
      "id": "77919296711259",
      "lotSize": 10000,
      "secType": 5,
      "name": "腾讯麦银一九购A.C",
      "listTime": "2019-09-10",
      "delisting": false,
      "listTimestamp": 1568044800
    },
    "warrantExData": {
      "type": 1,
      "owner": {
        "market": 1,
        "code": "00700"
      }
    }
  }, ..., {
    "basic": {
      "security": {
        "market": 1,
        "code": "53501"
      },
      "id": "81084687634685",
      "lotSize": 5000,
      "secType": 5,
      "name": "腾讯法兴二五牛I",
      "listTime": "2021-09-14",
      "delisting": false,
      "listTimestamp": 1631548800
    },
    "warrantExData": {
      "type": 3,
      "owner": {
        "market": 1,
        "code": "00700"
      }
    }
  }]
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 10 次获取证券关联数据接口
* 当获取正股相关窝轮时，不受上述限频限制
:::

---

# 获取期货合约资料

`GetFutureInfo(req);`

* **介绍**

    获取期货合约资料

* **参数**

```protobuf

message C2S
{
	repeated Qot_Common.Security securityList = 1; //股票列表
}

message Request
{
	required C2S c2s = 1;
}
```

>    - 股票结构参见 [Security](./quote.md#1377)

* **返回**

```protobuf
//交易时间
message TradeTime
{
    optional double begin = 1; // 开始时间，以分钟为单位
	optional double end = 2; // 结束时间，以分钟为单位
}

//期货合约资料的列表
message FutureInfo
{
	required string name = 1; // 合约名称
	required Qot_Common.Security security = 2; // 合约代码
	required string lastTradeTime = 3; //最后交易日，只有非主连期货合约才有该字段
	optional double lastTradeTimestamp = 4; //最后交易日时间戳，只有非主连期货合约才有该字段
	optional Qot_Common.Security owner = 5; //标的股 股票期货和股指期货才有该字段
	required string ownerOther = 6; //标的 
	required string exchange = 7; //交易所
	required string contractType = 8; //合约类型
	required double contractSize = 9; //合约规模
	required string contractSizeUnit = 10; //合约规模的单位
	required string quoteCurrency = 11; //报价货币
	required double minVar = 12; //最小变动单位
	required string minVarUnit = 13; //最小变动单位的单位（该字段已废弃）
	optional string quoteUnit = 14; //报价单位
	repeated TradeTime tradeTime = 15; //交易时间
	required string timeZone = 16; //所在时区
	required string exchangeFormatUrl = 17; //交易所规格
    optional Qot_Common.Security origin = 18; //实际合约代码
}

message S2C
{
	repeated FutureInfo futureInfoList = 1; //期货合约资料的列表
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType，返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetFutureInfo(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功

            const req = {
                c2s: {
                    securityList:[{
                        market: QotMarket.QotMarket_HK_Future,
                        code: "MPImain",
                    },{
                        market: QotMarket.QotMarket_HK_Future,
                        code: "HAImain",
                    },],
                },
            };

            websocket.GetFutureInfo(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("FutureInfo: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
FutureInfo: errCode 0, retMsg , retType 0
{
  "futureInfoList": [{
    "name": "内房主连(2109)",
    "security": {
      "market": 1,
      "code": "MPImain"
    },
    "lastTradeTime": "",
    "ownerOther": "恒生中国内地地产指数",
    "exchange": "港交所",
    "contractType": "股指期货",
    "contractSize": 50,
    "contractSizeUnit": "指数点×港元",
    "quoteCurrency": "港元",
    "minVar": 0.5,
    "minVarUnit": "",
    "quoteUnit": "指数点",
    "tradeTime": [{
      "begin": 555,
      "end": 720
    }, {
      "begin": 780,
      "end": 990
    }],
    "timeZone": "CCT",
    "exchangeFormatUrl": "https://sc.hkex.com.hk/TuniS/www.hkex.com.hk/Products/Listed-Derivatives/Equity-Index/Sector-Index/Sector-Index-Futures?sc_lang=zh-CN"
  }, {
    "name": "海通证券主连(2109)",
    "security": {
      "market": 1,
      "code": "HAImain"
    },
    "lastTradeTime": "",
    "owner": {
      "market": 1,
      "code": "06837"
    },
    "ownerOther": "海通证券",
    "exchange": "港交所",
    "contractType": "股票期货",
    "contractSize": 10000,
    "contractSizeUnit": "股",
    "quoteCurrency": "港元",
    "minVar": 0.01,
    "minVarUnit": "",
    "quoteUnit": "每股/港元",
    "tradeTime": [{
      "begin": 570,
      "end": 720
    }, {
      "begin": 780,
      "end": 960
    }],
    "timeZone": "CCT",
    "exchangeFormatUrl": "https://www.hkex.com.hk/Products/Listed-Derivatives/Single-Stock/Stock-Futures?sc_lang=zh-HK",
    "security": {
      "market": 1,
      "code": "HAI2112"
    }
  }]
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次获取期货合约资料接口
* 每次请求的代码列表中，期货个数上限为 200 个
:::

---

# 条件选股

`StockFilter(req);`

* **介绍**

    条件选股

* **参数**

```protobuf
// 使用以下6种结构(BaseFilter、AcumulateFilter、FinancialFilter、BaseData、AcumulateData、FinancialData)的用户请注意，由于属性字段名“field”与C#protocol buf保留的函数名冲突，Futu API将从3.18版本开始将该字段重命名为“fieldName”。请注意修改相应界面中使用的字段名称。

// 简单属性筛选
message BaseFilter 
{ 
	required int32 fieldName = 1; // StockField 简单属性
	optional double filterMin = 2; // 区间下限（闭区间），不传代表下限为 -∞
	optional double filterMax = 3; // 区间上限（闭区间），不传代表上限为 +∞
	optional bool isNoFilter = 4; // 该字段是否不需要筛选，True：不筛选，False：筛选。不传默认不筛选
	optional int32 sortDir = 5; // SortDir 排序方向，默认不排序。
}

// 累积属性筛选
message AccumulateFilter
{
	required int32 fieldName = 1; // AccumulateField 累积属性
	optional double filterMin = 2; // 区间下限（闭区间），不传代表下限为 -∞
	optional double filterMax = 3; // 区间上限（闭区间），不传代表上限为 +∞
	optional bool isNoFilter = 4; // 该字段是否不需要筛选，True：不筛选，False：筛选。不传默认不筛选
	optional int32 sortDir = 5; // SortDir 排序方向，默认不排序。
	required int32 days = 6; // 近几日，累积时间
}

// 财务属性筛选
message FinancialFilter
{
	required int32 fieldName = 1; // FinancialField 财务属性
	optional double filterMin = 2; // 区间下限（闭区间），不传代表下限为 -∞
	optional double filterMax = 3; // 区间上限（闭区间），不传代表上限为 +∞
	optional bool isNoFilter = 4; // 该字段是否不需要筛选，True：不筛选，False：筛选。不传默认不筛选
	optional int32 sortDir = 5; // SortDir 排序方向，默认不排序。
	required int32 quarter = 6; // FinancialQuarter 财报累积时间
}

// 形态技术指标属性筛选
message PatternFilter
{
	required int32 fieldName = 1; // PatternField 形态技术指标属性
	required int32 klType = 2; // Qot_Common.KLType，K线类型，仅支持K_60M，K_DAY，K_WEEK，K_MON 四种时间周期
	optional bool isNoFilter = 3; // 该字段是否不需要筛选，True代表不筛选，False代表筛选。不传默认为不筛选
    optional int32 consecutivePeriod = 4; // 筛选连续周期（consecutivePeriod）都符合条件的数据，填写范围为[1,12]
}

// 自定义技术指标属性筛选
message CustomIndicatorFilter
{
	required int32 firstFieldName = 1; // CustomIndicatorField 自定义技术指标属性
	required int32 secondFieldName = 2; // CustomIndicatorField 自定义技术指标属性
	required int32 relativePosition = 3; // RelativePosition 相对位置
	optional double fieldValue = 4; // 自定义数值
	required int32 klType = 5; // Qot_Common.KLType，K线类型，仅支持K_60M，K_DAY，K_WEEK，K_MON 四种时间周期	
	optional bool isNoFilter = 6; // 该字段是否不需要筛选，True代表不筛选，False代表筛选。不传默认为不筛选
    repeated int32 firstFieldParaList = 7; // 自定义指标参数。根据指标类型进行传参：1. MA：[平均移动周期] 2.EMA：[指数移动平均周期] 3.RSI：[RSI 指标周期] 4.MACD：[快速平均线值, 慢速平均线值, DIF值] 5.BOLL：[均线周期, 偏移值] 6.KDJ：[RSV 周期, K 值计算周期, D 值计算周期]
	repeated int32 secondFieldParaList = 8; // 自定义指标参数。根据指标类型进行传参：1. MA：[平均移动周期] 2.EMA：[指数移动平均周期] 3.RSI：[RSI 指标周期] 4.MACD：[快速平均线值, 慢速平均线值, DIF值] 5.BOLL：[均线周期, 偏移值] 6.KDJ：[RSV 周期, K 值计算周期, D 值计算周期]
	optional int32 consecutivePeriod = 9; // 筛选连续周期（consecutivePeriod）都符合条件的数据，填写范围为[1,12]
}

message C2S
{
    required int32 begin = 1; // 数据起始点
    required int32 num =  2;  // 请求数据个数，最大200        
	required int32 market= 3; // Qot_Common::QotMarket 股票市场，支持沪股和深股，且沪股和深股不做区分都代表 A 股市场。
	// 以下为筛选条件，可选字段，不填表示不过滤
	optional Qot_Common.Security plate = 4; // 板块
	repeated BaseFilter baseFilterList = 5; // 简单指标过滤器
	repeated AccumulateFilter accumulateFilterList = 6; // 累积指标过滤器 累积属性的同一筛选条件数量上限 10 个
	repeated FinancialFilter financialFilterList = 7; // 财务指标过滤器
	repeated PatternFilter patternFilterList = 8; // 形态技术指标过滤器
	repeated CustomIndicatorFilter customIndicatorFilterList = 9; // 自定义技术指标过滤器
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377) 
>    - 市场类型参见 [QotMarket](./quote.md#427) 
>    - 简单属性筛选条件参见 [StockField](./quote.md#860) 
>    - 累积属性筛选条件参见 [AccumulateField](./quote.md#4370) 
>    - 财务属性筛选条件参见 [FinancialField](./quote.md#8542) 
>    - 自定义技术指标属性筛选条件参见 [CustomIndicatorField](./quote.md#2057)
>    - 形态技术指标属性筛选条件参见 [PatternField](./quote.md#159)
>    - 财报时间周期参见 [FinancialQuarter](./quote.md#2253) 
>    - 排序方向参见 [SortDir](./quote.md#5471)
>    - 相对位置参见 [RelativePosition](./quote.md#2453) 
>    - K线类型参见 [KLType](./quote.md#4119)  

* **返回**

```protobuf
// 简单属性数据
message BaseData 
{ 
	required int32 fieldName = 1; // StockField 简单属性
    required double value = 2;
}

// 累积属性数据
message AccumulateData
{
	required int32 fieldName = 1; // AccumulateField 累积属性
    required double value = 2;
	required int32 days = 3; // 近几日，累积时间
}

// 财务属性数据
message FinancialData
{
	required int32 fieldName = 1; // FinancialField 财务属性
    required double value = 2;
	required int32 quarter = 3; // FinancialQuarter 财报累积时间
}

// 自定义技术指标属性数据
message CustomIndicatorData
{
	required int32 fieldName = 1; // CustomIndicatorField 自定义技术指标属性
	required double value = 2; 
	required int32 klType = 3; // Qot_Common.KLType，K线类型，仅支持K_60M，K_DAY，K_WEEK，K_MON 四种时间周期
    repeated int32 fieldParaList = 4; // 自定义指标参数 根据指标类型进行传参：1. MA：[平均移动周期] 2.EMA：[指数移动平均周期] 3.RSI：[RSI 指标周期] 4.MACD：[快速平均线值, 慢速平均线值, DIF值] 5.BOLL：[均线周期, 偏移值] 6.KDJ：[RSV 周期, K 值计算周期, D 值计算周期]
}

// 返回的股票数据
message StockData  
{
    required Qot_Common.Security security = 1; // 股票
	required string name = 2; // 股票名称
    repeated BaseData baseDataList = 3; // 筛选后的简单指标属性数据
	repeated AccumulateData accumulateDataList = 4; // 筛选后的累积指标属性数据
	repeated FinancialData financialDataList = 5; // 筛选后的财务指标属性数据
    repeated CustomIndicatorData customIndicatorDataList = 6; // 自定义技术指标属性数据
    // CustomIndicatorFilter 中的 firstFieldName 和 secondFieldName 的数值会在这个列表中分开返回
}

message S2C
{
    required bool lastPage = 1; // 是否最后一页了,false:非最后一页,还有窝轮记录未返回; true:已是最后一页
	required int32 allCount = 2; // 该条件请求所有数据的个数
    repeated StockData dataList = 3; // 返回的股票数据列表
}

message Response
{
	required int32 retType = 1 [default = -400]; // RetType,返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	optional S2C s2c = 4;
}
```
>    - 股票结构参见 [Security](./quote.md#1377) 
>    - 简单属性筛选条件参见 [StockField](./quote.md#860) 
>    - 累积属性筛选条件参见 [AccumulateField](./quote.md#4370) 
>    - 财务属性筛选条件参见 [FinancialField](./quote.md#8542) 
>    - 财报时间周期参见 [FinancialQuarter](./quote.md#2253) 
>    - 自定义技术指标属性筛选条件参见 [CustomIndicatorField](./quote.md#2057)
>    - K线类型参见 [KLType](./quote.md#4119)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotStockFilter(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功

            const req = {
                c2s: {
                    begin: 0, 
                    num: 2,
                    market: QotMarket.QotMarket_HK_Security,
                },
            };

            websocket.StockFilter(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("StockFilter: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
StockFilter: errCode 0, retMsg , retType 0
{
  "lastPage": false,
  "allCount": 2436,
  "dataList": [{
    "security": {
      "market": 1,
      "code": "08579"
    },
    "name": "万亚企业控股"
  }, {
    "security": {
      "market": 1,
      "code": "09869"
    },
    "name": "海伦司"
  }]
}
stop
```

:::tip 提示
* 利用[获取子板块列表函数](../quote/get-plate-list.md) 获取子板块代码，条件选股支持的板块分别为
    1. 港股的行业板块和概念板块。
    2. 美股的行业板块
    3. 沪深的行业板块，概念板块和地域板块
* 支持的板块指数代码
    代码|说明
    :-|:-
    HK.Motherboard|港股主板
    HK.GEM|港股创业板
    HK.BK1911|H 股主板
    HK.BK1912|H 股创业板
    US.NYSE|纽交所
    US.AMEX|美交所
    US.NASDAQ|纳斯达克
    SH.3000000|上海主板
    SZ.3000001|深证主板
    SZ.3000004|深证创业板
:::

:::tip 接口限制
* 港股 BMP 权限不支持条件选股功能
* 每 30 秒内最多请求 10 次条件选股接口
* 每页返回的筛选结果最多 200 个
* 建议筛选条件不超过 250 个，否则可能会出现“业务处理超时没返回”
* 累积属性的同一筛选条件数量上限 10 个
* 如果使用“最新价”等动态数据作为排序字段，在多页获取的间隙，数据的排序有可能发生变化
* 非同类指标不支持比较，仅限于同类指标之间建立比较关系，跨不同类型的指标比较会报错。例如：MA5 和 MA10 可以建立关系。MA5和EMA10不能建立关系。
* 自定义指标属性的同一类筛选条件超出数量上限10个
* 简单属性，财务属性，形态属性不支持对同一字段重复指定筛选条件
* 条件选股暂不支持美股盘前盘后、夜盘，筛选结果均按照盘中数据返回
:::

---

# 筛选正股

`GetStockScreen(req);`


* **介绍**

    条件选股 V2

* **参数**

```protobuf
message Boundary
{
    required double value = 1;
    optional bool includes = 2;     // 是否闭区间，默认 true
}

message Interval
{
    optional Boundary filterMin = 1;
    optional Boundary filterMax = 2;
}

// ===== 各类 PropertyXxx =====
message PropertyBasic         { required int32 name = 1; }
message PropertySimple        { required int32 name = 1; optional int32 unit = 2; }
message PropertyCumulative    {
    required int32 name = 1;
    required int32 days = 2;
    optional int32 periodAverage = 3;
    optional int32 unit = 4;
}
message PropertyFinancial     {
    required int32 name = 1;
    optional int32 term = 2;
    optional int32 year = 3;
    optional int32 duration = 4;
    optional int32 periodAverage = 5;
    optional int32 futureDuration = 6;
    optional int32 unit = 7;
}
message PropertyIndicator     {
    required int32 name = 1;
    optional int32 period = 2;
    repeated int32 indicatorParams = 3;
}
message PropertyFeatured      {
    required int32 name = 1;
    optional int32 period = 2;
    optional int32 rangePeriod = 3;
    optional int32 firstCustomParam = 4;
}
message PropertyBroker        {
    required int32 name = 1;
    optional int32 days = 2;
    optional string param = 3;
}
message PropertyOption        {
    required int32 name = 1;
    optional int32 period = 2;
    optional string param = 3;
}
message PropertyKlineShape    {
    required int32 name = 1;
    optional int32 period = 2;
}

// ===== 各类 QueryXxx =====
message SimpleFieldQuery
{
    required int32 simpleField = 1;
    repeated int32 screenValueList = 2;
}

message PlateInfo
{
    repeated string plateIdList = 1;
    optional string parentPlateId = 2;
}

message PlateQuery       { repeated PlateInfo plateList = 1; }

message SimplePropertyQuery
{
    required PropertySimple property = 1;
    optional Boundary filterMin = 2;
    optional Boundary filterMax = 3;
}

message CumulativePropertyQuery
{
    required PropertyCumulative property = 1;
    optional Boundary filterMin = 2;
    optional Boundary filterMax = 3;
    optional int32 continuousPeriod = 4;
}

message FinancialPropertyQuery
{
    required PropertyFinancial property = 1;
    optional Boundary filterMin = 2;
    optional Boundary filterMax = 3;
    optional int32 continuousPeriod = 4;
}

message IndicatorPositionalQuery
{
    required int32 firstIndicatorName = 1;
    required int32 periodType = 2;
    required int32 position = 3;
    optional int32 secondIndicator = 4;
    optional int32 secondValue = 5;
    repeated int32 firstIndicatorParams = 6;
    repeated int32 secondIndicatorParams = 7;
    optional int32 continuousPeriod = 8;
    repeated Interval intervals = 9;
}

message IndicatorPatternQuery
{
    required int32 name = 1;
    required int32 periodType = 2;
    optional int32 continuousPeriod = 3;
    optional bool isMatching = 4;
    repeated int32 subPatterns = 5;
}

message FeaturedPropertyQuery
{
    required PropertyFeatured property = 1;
    repeated Interval intervals = 2;
    repeated int32 valueSet = 3;
}

message BrokerHoldingsQuery
{
    required PropertyBroker property = 1;
    repeated Interval intervals = 2;
}

message KlineShapeQuery
{
    required PropertyKlineShape property = 1;
    repeated int32 valueSet = 2;
}

message OptionQuery
{
    required PropertyOption property = 1;
    repeated Interval intervals = 2;
}

// ===== 一条筛选条件 (oneof 多选一) =====
message ScreenQuery
{
    optional SimpleFieldQuery simpleFieldQuery = 1;
    optional PlateQuery plateQuery = 2;
    optional SimplePropertyQuery simplePropertyQuery = 3;
    optional CumulativePropertyQuery cumulativePropertyQuery = 4;
    optional FinancialPropertyQuery financialPropertyQuery = 5;
    optional IndicatorPositionalQuery indicatorPositionalQuery = 6;
    optional IndicatorPatternQuery indicatorPatternQuery = 7;
    optional FeaturedPropertyQuery featuredPropertyQuery = 8;
    optional BrokerHoldingsQuery brokerHoldingsQuery = 9;
    optional KlineShapeQuery klineShapeQuery = 10;
    optional OptionQuery optionQuery = 11;
}

// ===== 取回字段 =====
message RetrieveQuery
{
    optional PropertyBasic basicProperty = 1;
    optional PropertySimple simpleProperty = 2;
    optional PropertyCumulative cumulativeProperty = 3;
    optional PropertyFinancial financialProperty = 4;
    optional PropertyIndicator indicatorProperty = 5;
    optional PropertyFeatured featuredProperty = 6;
    optional PropertyBroker brokerProperty = 7;
    optional PropertyOption optionProperty = 8;
    optional PropertyKlineShape klineShapeProperty = 9;
}

// ===== 排序定义 =====
message Sort
{
    required int32 direction = 1;   // 1=ASC, 2=DESC, 3=ABS_ASC, 4=ABS_DESC
    optional PropertyBasic basicProperty = 2;
    optional PropertySimple simpleProperty = 3;
    optional PropertyCumulative cumulativeProperty = 4;
    optional PropertyFinancial financialProperty = 5;
    optional PropertyIndicator indicatorProperty = 6;
    optional PropertyFeatured featuredProperty = 7;
    optional PropertyBroker brokerProperty = 8;
    optional PropertyOption optionProperty = 9;
    optional PropertyKlineShape klineShapeProperty = 10;
}

message C2S
{
    repeated ScreenQuery filterList = 1;
    repeated RetrieveQuery retrieveList = 2;
    repeated int64 watchlistStockIds = 3;
    optional Sort sort = 4;             // 单字段排序
    optional int32 pageFrom = 5;
    optional int32 pageCount = 6;
    repeated Sort sortList = 7;         // 多字段排序，非空时优先于 sort
}

message Request
{
    required C2S c2s = 1;
}
```

* **返回**

```protobuf
// 单条结果值: valueType=1 时取 sval, =2 取 ival, =3 取 aval, =4 取 dval
message ResultPropertyBasic
{
    required PropertyBasic property = 1;
    optional int32 valueType = 2;
    optional string sval = 3;
    optional int64 ival = 4;
    repeated int64 aval = 5;
    optional double dval = 6;
    optional string enumTypeName = 7;
    optional string enumName = 8;
}
// 其余 ResultPropertySimple / Cumulative / Financial / Indicator / Featured / Broker / Option / KlineShape
// 结构与 ResultPropertyBasic 相同，仅 property 类型不同。Financial 额外包含 endTime。

message RspItemResult
{
    optional ResultPropertyBasic basicPropertyResult = 1;
    optional ResultPropertySimple simplePropertyResult = 2;
    optional ResultPropertyCumulative cumulativePropertyResult = 3;
    optional ResultPropertyFinancial financialPropertyResult = 4;
    optional ResultPropertyIndicator indicatorPropertyResult = 5;
    optional ResultPropertyFeatured featuredPropertyResult = 6;
    optional ResultPropertyBroker brokerPropertyResult = 7;
    optional ResultPropertyOption optionPropertyResult = 8;
    optional ResultPropertyKlineShape klineShapePropertyResult = 9;
}

message RspItem
{
    required int64 stockId = 1;
    repeated RspItemResult results = 2;
}

message S2C
{
    required bool lastPage = 1;
    required int32 allCount = 2;
    repeated RspItem dataList = 3;
}

message Response
{
    required int32 retType = 1 [default = -400];
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3252

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetStockScreen(){
    const { RetType } = Common
    // SimpleField / ScrMarket / SimpleProperty 为数值常量，完整列表见 quote.md「筛选 V2」；下同
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            // 港股最新价 >= 10、市值 >= 100 亿，按市值降序取回代码/名称/价格/市值
            const req = {
                c2s: {
                    filterList: [
                        { simpleFieldQuery: { simpleField: 1 /* SimpleField.MARKET 市场 */, screenValueList: [1 /* ScrMarket.HK */] } },
                        { simplePropertyQuery: { property: { name: 2201 /* SimpleProperty.PRICE */ }, filterMin: { value: 10, includes: true } } },
                        { simplePropertyQuery: { property: { name: 2301 /* SimpleProperty.MARKET_CAP */ }, filterMin: { value: 10000000000, includes: true } } }
                    ],
                    retrieveList: [
                        { basicProperty: { name: 1101 } },
                        { basicProperty: { name: 1102 } },
                        { simpleProperty: { name: 2201 /* SimpleProperty.PRICE */ } },
                        { simpleProperty: { name: 2301 /* SimpleProperty.MARKET_CAP */ } }
                    ],
                    sort: { direction: 2, simpleProperty: { name: 2301 /* SimpleProperty.MARKET_CAP */ } },
                    pageFrom: 0,
                    pageCount: 5,
                },
            };
            websocket.GetStockScreen(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetStockScreen: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetStockScreen()
```

* **Output**

``` JavaScript
GetStockScreen: errCode 0, retMsg , retType 0
{
  "lastPage": true,
  "allCount": 1,
  "dataList": [
    {
      "stockId": "54047868453564",
      "results": [
        { "basicPropertyResult": { "property": { "name": 1101 }, "valueType": 1, "sval": "00700" } },
        { "basicPropertyResult": { "property": { "name": 1102 }, "valueType": 1, "sval": "腾讯控股" } },
        { "simplePropertyResult": { "property": { "name": 2201 }, "valueType": 4, "dval": 460.0 } },
        { "simplePropertyResult": { "property": { "name": 2301 }, "valueType": 4, "dval": 4194280264040.0 } }
      ]
    }
  ]
}
```

:::tip 接口限制
* 每 30 秒内最多请求 10 次条件选股接口
:::

---

# 获取板块内股票列表

`GetPlateSecurity(req);`

* **介绍**

    获取板块内的股票

* **参数**

```protobuf
message C2S
{
    required Qot_Common.Security plate = 1; //板块
    optional int32 sortField = 2;//Qot_Common.SortField，根据哪个字段排序，不填默认 Code 排序
    optional bool ascend = 3;//升序 true，降序 false，不填默认升序

}

message Request
{
    required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 排序字段参见 [SortField](./quote.md#2930)

* **返回**

```protobuf
message S2C
{
    repeated Qot_Common.SecurityStaticInfo staticInfoList = 1; //板块下的股票静态信息
}

message Response
{
    required int32 retType = 1 [default = -400]; //RetType，返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;

    optional S2C s2c = 4;
}
```
>    - 股票静态信息结构参见 [SecurityStaticInfo](./quote.md#609)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetPlateSecurity(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功

            const req = {
                c2s: {
                    plate:{
                        market: QotMarket.QotMarket_HK_Security,
                        code: "Motherboard",
                    },
                },
            };

            websocket.GetPlateSecurity(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("PlateSecurity: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
PlateSecurity: errCode 0, retMsg , retType 0
{
  "staticInfoList": [{
    "basic": {
      "security": {
        "market": 1,
        "code": "00001"
      },
      "id": "4440996184065",
      "lotSize": 500,
      "secType": 3,
      "name": "长和",
      "listTime": "2015-03-18",
      "delisting": false,
      "listTimestamp": 1426608000
    }
  }, {
    "basic": {
      "security": {
        "market": 1,
        "code": "00002"
      },
      "id": "2",
      "lotSize": 500,
      "secType": 3,
      "name": "中电控股",
      "listTime": "1970-01-01",
      "delisting": false,
      "listTimestamp": 0
    }
  }, ..., {
    "basic": {
      "security": {
        "market": 1,
        "code": "87001"
      },
      "id": "64819646518233",
      "lotSize": 1000,
      "secType": 4,
      "name": "汇贤产业信托",
      "listTime": "2011-04-29",
      "delisting": false,
      "listTimestamp": 1304006400
    }
  }]
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 10 次获取板块内股票列表接口
:::

::: details  常用的板块、指数代码
代码|说明
:-|:-
HK.HSI Constituent Stocks|恒指成份股
HK.HSCEI Stock|国指成份股
HK.Motherboard|港股主板
HK.GEM|港股创业板
HK.LIST1910|所有港股
HK.LIST1911|主板 H 股
HK.LIST1912|创业板 H 股
HK.Fund|ETF（港股基金）
HK.LIST1600|热度榜（港）
HK.LIST1921|已上市新股-港股
SH.LIST3000000|上海主板
SH.LIST0901|上证 B 股
SH.LIST0902|深证 B 股
SH.LIST3000002|沪深指数
SH.LIST3000005|全部 A 股（沪深）
SH.LIST0600|热度榜（沪深）
SH.LIST0992|科创板
SH.LIST0921|已上市新股-A 股	
SZ.LIST3000001|深证主板
SZ.LIST3000003|中小板
SZ.LIST3000004|创业板（深）
US.USAALL|全部美股
:::

---

# 获取板块列表

`GetPlateSet(req);`

* **介绍**

    获取板块列表

* **参数**

```protobuf
message C2S
{
    required int32 market = 1; //Qot_Common.QotMarket，股票市场
    required int32 plateSetType = 2; //Qot_Common.PlateSetType，板块集合的类型
}

message Request
{
    required C2S c2s = 1;
}
```
>    - 市场类型参见 [QotMarket](./quote.md#427)
>    - 板块集合类型枚举参见 [PlateSetType](./quote.md#1362)

* **返回**

```protobuf
message S2C
{
    repeated Qot_Common.PlateInfo plateInfoList = 1; //板块集合下的板块信息
}

message Response
{
    required int32 retType = 1 [default = -400]; //RetType，返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    
    optional S2C s2c = 4;
}
```
>    - 板块信息结构参见 [PlateInfo](./quote.md#2571)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetPlateSet(){
    const { RetType } = Common
    const { QotMarket, PlateSetType } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功

            const req = {
                c2s: {
                    market: QotMarket.QotMarket_HK_Security,
                    plateSetType: PlateSetType.PlateSetType_All,
                },
            };

            websocket.GetPlateSet(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("PlateSet: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
PlateSet: errCode 0, retMsg , retType 0
{
  "plateInfoList": [{
    "plate": {
      "market": 1,
      "code": "BK1000"
    },
    "name": "做空集合股"
  }, {
    "plate": {
      "market": 1,
      "code": "BK1001"
    },
    "name": "乳制品"
  }, ..., {
    "plate": {
      "market": 1,
      "code": "BK1998"
    },
    "name": "节假日概念"
  }]
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 10 次获取板块列表接口
:::

---

# 获取静态数据

`GetStaticInfo(req);`

* **介绍**

    获取静态数据

* **参数**

```protobuf
message C2S
{
    // 当 market 和 code_list 同时存在时，会忽略 market，仅对 code_list 进行查询。
	optional int32 market = 1; //Qot_Common.QotMarket，股票市场
	optional int32 secType = 2; //Qot_Common.SecurityType，股票类型
	repeated Qot_Common.Security securityList = 3; //股票，若该字段存在，忽略其他字段，只返回该字段股票的静态信息
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 股票结构参见[Security](./quote.md#1377)
>    - 行情市场参见[QotMarket](./quote.md#427)
>    - 股票类型参见[SecurityType](./quote.md#3325)

* **返回**

```protobuf
message S2C
{
	repeated Qot_Common.SecurityStaticInfo staticInfoList = 1; //静态信息
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType，返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 股票静态信息结构参见[SecurityStaticInfo](./quote.md#609)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetStaticInfo(){
    const { RetType } = Common
    const { QotMarket, PlateSetType } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功

            const req = {
                c2s: {
                    securityList: [{
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },],
                },
            };

            websocket.GetStaticInfo(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("StaticInfo: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
StaticInfo: errCode 0, retMsg , retType 0
{
  "staticInfoList": [{
    "basic": {
      "security": {
        "market": 1,
        "code": "00700"
      },
      "id": "54047868453564",
      "lotSize": 100,
      "secType": 3,
      "name": "腾讯控股",
      "listTime": "2004-06-16",
      "delisting": false,
      "listTimestamp": 1087315200
    }
  }]
}
stop
```

:::tip 提示
* 当传入程序无法识别的股票时（包括很久之前退市的股票和不存在的股票），此接口仍然返回股票信息，用“是否退市”字段来标识该股票不存在。统一处理为：代码正常显示，股票名显示为“未知股票”，其他字段均为默认值（整型默认是0，字符串默认是空字符串）。
* 此接口与其他的行情接口不同，其他接口遇到程序无法识别的股票时，会拒绝请求并返回错误描述“未知股票”。
* 获取期权数据（例如：希腊值、到期日、未平仓量），请使用 [获取快照](./get-market-snapshot.md)。
:::

---

# 获取 IPO 信息

`GetIpoList(req);`

* **介绍**

    获取指定市场的 IPO 信息

* **参数**

```protobuf
message C2S
{
	required int32 market = 1; // Qot_Common::QotMarket 股票市场，支持沪股和深股，且沪股和深股不做区分都代表 A 股市场。
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 行情市场参见 [QotMarket](./quote.md#427)

* **返回**

```protobuf
// IPO 基本数据
message BasicIpoData
{
	required Qot_Common.Security security = 1; // Qot_Common::QotMarket 股票市场，支持沪股和深股，且沪股和深股不做区分都代表 A 股市场。
	required string name = 2; // 股票名称
	optional string listTime = 3; // 上市日期字符串（格式：yyyy-MM-dd）
	optional double listTimestamp = 4; // 上市日期时间戳
};

// A 股 IPO 列表额外数据
message CNIpoExData 
{
	required string applyCode = 1; // 申购代码
	required int64 issueSize = 2; // 发行总数
	required int64 onlineIssueSize = 3; // 网上发行量
	required int64 applyUpperLimit = 4; // 申购上限
	required int64 applyLimitMarketValue = 5; // 顶格申购需配市值
	required bool isEstimateIpoPrice = 6; // 是否预估发行价
	required double ipoPrice = 7; // 发行价 预估值会因为募集资金、发行数量、发行费用等数据变动而变动，仅供参考。实际数据公布后会第一时间更新。
	required double industryPeRate = 8; // 行业市盈率
	required bool isEstimateWinningRatio = 9; // 是否预估中签率
	required double winningRatio = 10; // 中签率 该字段为百分比字段，默认不展示 %，如 20 实际对应 20%。预估值会因为募集资金、发行数量、发行费用等数据变动而变动，仅供参考。实际数据公布后会第一时间更新。
	required double issuePeRate = 11; // 发行市盈率
	optional string applyTime = 12; // 申购日期字符串（格式：yyyy-MM-dd）
	optional double applyTimestamp = 13; // 申购日期时间戳
	optional string winningTime = 14; // 公布中签日期字符串（格式：yyyy-MM-dd）
	optional double winningTimestamp = 15; // 公布中签日期时间戳
	required bool isHasWon = 16; // 是否已经公布中签号
	repeated WinningNumData winningNumData = 17; // Qot_GetIpoList::WinningNumData 中签号数据，对应 PC 中"公布中签日期的已公布"
};

// 中签号数据
message WinningNumData
{
	required string winningName = 1; // 分组名
    required string winningInfo = 2; // 中签号信息
}

// 港股 IPO 列表额外数据
message HKIpoExData
{
	required double ipoPriceMin = 1; // 最低发售价
	required double ipoPriceMax = 2; // 最高发售价
	required double listPrice = 3; // 上市价
	required int32 lotSize = 4; // 每手股数
	required double entrancePrice = 5; // 入场费
	required bool isSubscribeStatus = 6; // 是否为认购状态，True-认购中，False-待上市
	optional string applyEndTime = 7; // 截止认购日期字符串（格式：yyyy-MM-dd）
	optional double applyEndTimestamp = 8; // 截止认购日期时间戳 因需处理认购手续，富途认购截止时间会早于交易所公布的日期。
};

// 美股 IPO 列表额外数据
message USIpoExData  
{
	required double ipoPriceMin = 1; // 最低发行价
	required double ipoPriceMax = 2; // 最高发行价
	required int64 issueSize = 3; // 发行量
};

// 新加坡 IPO 额外数据
message SGIpoExData
{
	required double ipoPriceMin = 1; // 最低发行价
	required double ipoPriceMax = 2; // 最高发行价
	required int64 issueSize = 3; // 发行量
	optional string applyStartTime = 4; // 开始认购日期字符串
	optional double applyStartTimestamp = 5; // 开始认购日期时间戳
	optional string applyEndTime = 6; // 截止认购日期字符串
	optional double applyEndTimestamp = 7; // 截止认购日期时间戳
	optional string winningTime = 8; // 公布中签日期字符串
	optional double winningTimestamp = 9; // 公布中签日期时间戳
}

// 马来西亚 IPO 额外数据
message MYIpoExData
{
	required double offerPrice = 1; // 发行价
	required int64 issueSize = 2; // 发行量
	optional string applyStartTime = 3; // 开始认购日期字符串
	optional double applyStartTimestamp = 4; // 开始认购日期时间戳
	optional string applyEndTime = 5; // 截止认购日期字符串
	optional double applyEndTimestamp = 6; // 截止认购日期时间戳
	optional string winningTime = 7; // 公布中签日期字符串
	optional double winningTimestamp = 8; // 公布中签日期时间戳
}

// 日本 IPO 额外数据
message JPIpoExData
{
	required double ipoPriceMin = 1; // 最低发行价
	required double ipoPriceMax = 2; // 最高发行价
	required int64 issueSize = 3; // 发行量
}

// 新股 IPO 数据
message IpoData
{	
	required BasicIpoData basic = 1; // IPO 基本数据	
	optional CNIpoExData cnExData = 2; // A 股 IPO 额外数据
	optional HKIpoExData hkExData = 3; // 港股 IPO 额外数据
	optional USIpoExData usExData = 4; // 美股 IPO 额外数据
	optional SGIpoExData sgExData = 5; // 新加坡 IPO 额外数据
	optional MYIpoExData myExData = 6; // 马来西亚 IPO 额外数据
	optional JPIpoExData jpExData = 7; // 日本 IPO 额外数据
};

message S2C
{
	repeated IpoData ipoList = 1; // 新股 IPO 数据
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType，返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetIpoList(){
	const { RetType } = Common
	const { QotMarket } = Qot_Common
	let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
	let websocket = new ftWebsocket();

	websocket.onlogin = (ret, msg)=>{
		if (ret) { // 登录成功

			const req = {
				c2s: {
					market: QotMarket.QotMarket_US_Security,
				},
			};

			websocket.GetIpoList(req)
			.then((res) => {
				let { errCode, retMsg, retType,s2c } = res
				console.log("IpoList: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
				if(retType == RetType.RetType_Succeed){
					let data = beautify(JSON.stringify(s2c), {
						indent_size: 2,
						space_in_empty_paren: true,
					});
					console.log(data);
				}
			})
			.catch((error) => {
				console.log("error:", error);
			});
		} else {
			console.log("error", msg);
		}
	};

	websocket.start(addr, port, enable_ssl, key);
	
	//关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
	//同时OpenD也限制了最多128条连接
	//也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
	setTimeout(()=>{ 
		websocket.stop();
		console.log("stop");
	}, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
IpoList: errCode 0, retMsg , retType 0
{
  "ipoList": [{
    "basic": {
      "security": {
        "market": 11,
        "code": "FHLTU"
      },
      "name": "Future Health ESG Corp.",
      "listTime": "2021-09-10",
      "listTimestamp": 1631246400
    },
    "usExData": {
      "ipoPriceMin": 10,
      "ipoPriceMax": 10,
      "issueSize": "20000000"
    }
  }, {
    "basic": {
      "security": {
        "market": 11,
        "code": "FLAG.U"
      },
      "name": "FIRST LIGHT ACQUISITION GROUP, INC.",
      "listTime": "2021-09-10",
      "listTimestamp": 1631246400
    },
    "usExData": {
      "ipoPriceMin": 10,
      "ipoPriceMax": 10,
      "issueSize": "20000000"
    }
  }, ..., {
    "basic": {
      "security": {
        "market": 11,
        "code": "ROXA"
      },
      "name": "ROX FINANCIAL LP",
      "listTime": "2021-09-30",
      "listTimestamp": 1632974400
    },
    "usExData": {
      "ipoPriceMin": 10,
      "ipoPriceMax": 10,
      "issueSize": "8300000"
    }
  }]
}
stop
```

::: tip 接口限制
* 每 30 秒内最多请求 10 次获取 IPO 信息接口
:::

---

# 获取全局市场状态

`GetGlobalState(req);`

* **介绍**

    获取全局状态

* **参数**

```protobuf
message C2S
{
	required uint64 userID = 1; //历史原因，目前已废弃，填0即可
}

message Request
{
	required C2S c2s = 1;
}
```

* **返回**

```protobuf
message S2C
{
	required int32 marketHK = 1; //Qot_Common.QotMarketState,港股主板市场状态
	required int32 marketUS = 2; //Qot_Common.QotMarketState,美股 Nasdaq 市场状态 
	required int32 marketSH = 3; //Qot_Common.QotMarketState,沪市状态 
	required int32 marketSZ = 4; //Qot_Common.QotMarketState,深市状态 
	required int32 marketHKFuture = 5; //Qot_Common.QotMarketState,港股期货市场状态 
	optional int32 marketUSFuture = 15; //Qot_Common.QotMarketState,美国期货市场状态
	optional int32 marketSGFuture = 17; //Qot_Common.QotMarketState,新加坡期货市场状态 
	optional int32 marketJPFuture = 18; //Qot_Common.QotMarketState,日本期货市场状态 
	optional int32 marketSG = 19; //Qot_Common.QotMarketState,新加坡市场状态
	optional int32 marketMY = 20; //Qot_Common.QotMarketState,马来西亚市场状态
	optional int32 marketJP = 21; //Qot_Common.QotMarketState,日本市场状态
	required bool qotLogined = 6; //是否登录行情服务器
	required bool trdLogined = 7; //是否登录交易服务器
	required int32 serverVer = 8; //版本号
	required int32 serverBuildNo = 9; //buildNo
	required int64 time = 10; //当前服务器时间
	optional double localTime = 11; //当前本地时间
	optional Common.ProgramStatus programStatus = 12; //当前程序状态
	optional string qotSvrIpAddr = 13;
	optional string trdSvrIpAddr = 14;
	optional uint64 connID = 16; //此连接的连接 ID，连接的唯一标识
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType,返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 市场状态枚举参见 [QotMarketState](./quote.md#1252)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function GetGlobalState(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功

            const req = {
                c2s: {
                    userID: 0,
                },
            };

            websocket.GetGlobalState(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("GlobalState: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
GlobalState: errCode 0, retMsg , retType 0
{
  "marketHK": 6,
  "marketUS": 8,
  "marketSH": 6,
  "marketSZ": 6,
  "marketHKFuture": 15,
  "qotLogined": true,
  "trdLogined": true,
  "serverVer": 507,
  "serverBuildNo": 1908,
  "time": "1631261759",
  "localTime": 1631261759.095172,
  "programStatus": {
    "type": "ProgramStatusType_Ready"
  },
  "qotSvrIpAddr": "119.29.48.17",
  "trdSvrIpAddr": "106.55.66.8",
  "marketUSFuture": 23,
  "connID": "6842007721202028582",
  "marketSGFuture": 13,
  "marketJPFuture": 13
}
stop
```

---

# 获取交易日历

`RequestTradeDate(req);`

* **介绍**

    请求指定市场 / 指定标的的交易日历。  
    注意：该交易日是通过自然日剔除周末和节假日得到，未剔除临时休市数据。

* **参数**

```protobuf
message C2S
{
	//当 market 和 security 同时存在时，会忽略 market，仅对 security 进行查询。
    required int32 market = 1; //Qot_Common.TradeDateMarket，要查询的市场
	required string beginTime = 2; //开始时间字符串（格式：yyyy-MM-dd）
	required string endTime = 3; //结束时间字符串（格式：yyyy-MM-dd）
    optional Qot_Common.Security security = 4; // 指定标的
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 交易日市场类型枚举参见 [TradeDateMarket](./quote.md#940)

* **返回**

```protobuf
message TradeDate
{
	required string time = 1; //时间字符串（格式：yyyy-MM-dd）
	optional double timestamp = 2; //时间戳
	optional int32 tradeDateType = 3; //Qot_Common.TradeDateType，交易时间类型
}

message S2C
{
	repeated TradeDate tradeDateList = 1; //交易日，注意该交易日是通过自然日去除周末以及节假日得到，不包括临时休市数据。
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType，返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 交易日类型枚举参见 [TradeDateType](./quote.md#6676)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotRequestTradeDate(){
    const { RetType } = Common
    const { TradeDateMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功

            const req = {
                c2s: {
                    market: TradeDateMarket.TradeDateMarket_HK,
                    beginTime: "2021-08-05",
                    endTime: "2021-08-10",
                },
            };

            websocket.RequestTradeDate(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("TradeDate: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
TradeDate: errCode 0, retMsg , retType 0
{
  "tradeDateList": [{
    "time": "2021-08-05",
    "timestamp": 1628092800,
    "tradeDateType": 0
  }, {
    "time": "2021-08-06",
    "timestamp": 1628179200,
    "tradeDateType": 0
  }, {
    "time": "2021-08-09",
    "timestamp": 1628438400,
    "tradeDateType": 0
  }, {
    "time": "2021-08-10",
    "timestamp": 1628524800,
    "tradeDateType": 0
  }]
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 30 次获取交易日接口。
* 历史交易日历提供过去 10 年的数据，未来交易日历提供到今年 12 月 31 日 (举例：今天的日期是 2021 年 7 月 6 日，我们仅提供 2011-07-06 到 2021-12-31 期间的交易日历)。
:::

---

﻿# 搜索行情标的

`GetSearchQuote(req);`

* **介绍**

    按关键词搜索行情标的，返回匹配的标的列表。

* **参数**

```protobuf
message C2S
{
    required string keyword = 1;      //搜索词，如 lite
    optional int32 max_count = 2;     //本次请求的最大返回条数，默认10条，最大100条
    optional Qot_Common.QotHeader header = 100; //行情公共参数头
}

message Request
{
    required C2S c2s = 1;
}
```

* **返回**

```protobuf
message SearchQuote
{
    optional int32 market = 1;        //Qot_Common.QotMarket，市场类型
    optional string code = 2;         //股票代码，如 LITE / 01936
    optional string name = 3;         //股票名称，如 Lumentum / 利特米
    optional int32 sec_type = 4;      //Qot_Common.SecurityType，股票类型
    optional bool is_watched = 5;     //是否已在自选（需登录态）
}

message S2C
{
    repeated SearchQuote searchQuoteList = 1; //搜索行情列表
}

message Response
{
    required int32 retType = 1 [default = -400]; //RetType，返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 行情市场参见 [QotMarket](./quote.md#427)
>    - 股票类型参见 [SecurityType](./quote.md#3325)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetSearchQuote(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: {
                    keyword: "lite",
                    maxCount: 10,
                },
            };

            websocket.GetSearchQuote(req)
            .then((res) => {
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetSearchQuote: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetSearchQuote()
```

:::tip 接口限制
* 每 30 秒内最多请求 10 次搜索行情标的接口。
:::

---

﻿# 搜索资讯

`GetSearchNews(req);`

* **介绍**

    按关键词搜索资讯。

* **参数**

```protobuf
message C2S
{
    required string keyword = 1;       //搜索词，如 lite
    optional int32 max_count = 2;      //本次请求的最大返回条数，默认10条，最大100条
    optional int32 news_sub_type = 3;  //NewsSubType，资讯子类型，默认 NewsSubType_ALL
}

message Request
{
    required C2S c2s = 1;
}
```
>    - 资讯子类型枚举参见 [NewsSubType](./quote.md#320)

* **返回**

```protobuf
message SearchNews
{
    optional string title = 1;               //标题（含关键词）
    optional int32 news_sub_type = 2;        //NewsSubType，资讯子类型
    optional string source = 3;              //来源，如 富途资讯 / MT Newswires / Benzinga
    optional string publish_time = 4;        //发布时间
    optional int64 view_count = 5;           //浏览量
    repeated string related_securities = 6;  //关联标的列表，如 LITE.US，用于跳转
    optional string url = 7;                 //详情页链接
}

message S2C
{
    repeated SearchNews searchNewsList = 1; //搜索资讯列表
}

message Response
{
    required int32 retType = 1 [default = -400]; //RetType，返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)
>    - 资讯子类型枚举参见 [NewsSubType](./quote.md#320)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_GetSearchNews } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetSearchNews(){
    const { RetType } = Common
    const { NewsSubType } = Qot_GetSearchNews
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: {
                    keyword: "腾讯",
                    maxCount: 10,
                    newsSubType: NewsSubType.NewsSubType_ALL,
                },
            };

            websocket.GetSearchNews(req)
            .then((res) => {
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetSearchNews: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetSearchNews()
```

:::tip 接口限制
* 每 30 秒内最多请求 10 次搜索资讯接口。
:::

---

# 获取财报日历

`getEarningsCalendar(qotGetEarningsCalendar)`


* **介绍**

    协议请求与返回定义

* **参数**

```protobuf
// 财报日历排序类型
enum EarningsCalendarSortType {
    EarningsCalendarSortType_Unknown = 0;         //未知
    EarningsCalendarSortType_Hot = 1;             //热门(默认)
    EarningsCalendarSortType_MarketCap = 2;       //历史市值
    EarningsCalendarSortType_OptionVolume = 3;    //期权成交量(仅港美股)
    EarningsCalendarSortType_IV = 4;              //隐含波动率(仅港美股)
    EarningsCalendarSortType_IVRank = 5;          //IV等级(仅港美股)
    EarningsCalendarSortType_IVPercentile = 6;    //IV百分位数(仅港美股)
    EarningsCalendarSortType_RtMarketCap = 7;     //实时市值
}

// 财报日历发布类型
enum EarningsCalendarPubType {
    EarningsCalendarPubType_Unknown = -1;  //未知
    EarningsCalendarPubType_Regular = 0;   //盘中(未识别出时段)
    EarningsCalendarPubType_Before = 1;    //盘前
    EarningsCalendarPubType_After = 2;     //盘后
}

// 财报指标类型
enum EarningsCalendarEstimateType {
    EarningsCalendarEstimateType_Unknown = 0;   //未知
    EarningsCalendarEstimateType_EPS = 1;       //每股收益(EPS GAAP)
    EarningsCalendarEstimateType_Revenue = 2;   //总收入
    EarningsCalendarEstimateType_EBIT = 3;      //息税前利润
}

// 财报周期类型
enum EarningsCalendarPeriodType {
    EarningsCalendarPeriodType_Unknown = 0;      //未知
    EarningsCalendarPeriodType_Quarterly = 1;    //季度
    EarningsCalendarPeriodType_SemiAnnual = 2;   //半年度
    EarningsCalendarPeriodType_Annual = 3;       //年度
}

// 股票列表类型
enum EarningsCalendarStockListType {
    EarningsCalendarStockListType_Unknown = 0;    //未知
    EarningsCalendarStockListType_Watchlist = 1;  //自选股
    EarningsCalendarStockListType_Position = 2;   //持仓
    EarningsCalendarStockListType_Special = 3;    //特别关注
}

// 财报日历筛选因子类型
enum EarningsCalendarIndicatorType {
    EarningsCalendarIndicatorType_Unknown = 0;
    EarningsCalendarIndicatorType_PubType = 1;          //【确切值】发布类型(valueList, EarningsCalendarPubType)
    EarningsCalendarIndicatorType_EstimateType = 2;     //【确切值】指标类型(valueList, EarningsCalendarEstimateType)
    EarningsCalendarIndicatorType_MarketCap = 3;        //【范围】市值
    EarningsCalendarIndicatorType_StockListType = 4;    //【确切值】股票列表类型(valueList, EarningsCalendarStockListType)
    EarningsCalendarIndicatorType_OptionVolume = 5;     //【范围】期权成交量(仅港美股)
    EarningsCalendarIndicatorType_IV = 6;               //【范围】隐含波动率(%)(仅港美股)
    EarningsCalendarIndicatorType_IVRank = 7;           //【范围】IV等级(%)(仅港美股)
    EarningsCalendarIndicatorType_IVPercentile = 8;     //【范围】IV百分位数(%)(仅港美股)
    EarningsCalendarIndicatorType_RtMarketCap = 9;      //【范围】实时市值
}

// 财报日历筛选条件
message EarningsCalendarIndicator {
    required int32 indicatorType = 1;                           // EarningsCalendarIndicatorType
    optional Qot_OptionCommon.IndicatorValue indicatorValue = 2; // 筛选条件
}

// 财报预测数据
message EstimateData {
    optional int32 estimateType = 1;     // EarningsCalendarEstimateType
    optional double actualValue = 2;     // 实际值(已发布时有值)
    optional double predictValue = 3;    // 预测值
    optional string currency = 4;        // 货币单位(ISO 4217)
    optional int32 periodType = 5;       // EarningsCalendarPeriodType
}

// 财报日历项
message EarningsCalendarItem {
    required Qot_Common.Security security = 1;   // 股票
    optional string name = 2;                     // 股票名称
    optional string earningsDate = 3;             // 财报日期("yyyy-MM-dd")
    optional double earningsTimestamp = 4;        // 财报发布时间戳(秒)
    optional int32 pubType = 5;                   // EarningsCalendarPubType
    optional string periodText = 7;               // 财年周期(如"2025Q1")
    repeated EstimateData estimateList = 8;       // 预测数据列表
    // 期权字段(仅港美股)
    optional int64 optionVolume = 10;             // 期权成交量
    optional double iv = 11;                      // 隐含波动率(%)
    optional double ivRank = 12;                  // IV等级(%)
    optional double ivPercentile = 13;            // IV百分位数(%)
    // 行情字段
    optional double marketCap = 20;               // 实时市值
    optional double price = 21;                   // 最新价
}

message C2S {
    required int32 market = 1;      // Qot_Common.QotMarket (支持HK/US/CNSH/CNSZ/SG/JP/AU/CA)
    optional int32 sortType = 2;    // EarningsCalendarSortType (默认 Hot)
    optional string beginDate = 3;  // 开始日期，格式"yyyy-MM-dd"，不传默认今天(仅拉取当天)
    optional string endDate = 4;    // 结束日期，格式"yyyy-MM-dd"，不传则仅拉取beginDate当天；与beginDate间隔不超过7天
    repeated EarningsCalendarIndicator filterList = 5;  // 筛选条件(AND关系)
}

message S2C {
    repeated EarningsCalendarItem itemList = 1;
}

message Request {
    required C2S c2s = 1;
}

message Response {
    required int32 retType = 1 [default = -400]; //RetType，返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3401


* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetEarningsCalendar(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11111, false, "xxxxxx"];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: {
                    market: 11, // Qot_Common.QotMarket_US
                    beginDate: "2026-06-22",
                    endDate: "2026-06-22",
                },
            };
            websocket.GetEarningsCalendar(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetEarningsCalendar: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetEarningsCalendar()
```

* **Output**

``` JavaScript
GetEarningsCalendar: errCode 0, retMsg , retType 0
{
  "itemList": [
    { "security": { "market": 11, "code": "FRVO" }, "name": "FERVO ENERGY COMPANY", "earningsDate": "2026-06-22", "pubType": 1 },
    { "security": { "market": 11, "code": "BCKIY" }, "name": "BABCOCK INTERNATIONAL GROUP UNSP ADR", "earningsDate": "2026-06-22", "pubType": 0 },
    { "security": { "market": 11, "code": "POWW" }, "name": "Outdoor Holding", "earningsDate": "2026-06-22", "pubType": 1 }
  ]
}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取宏观指标列表

`getMacroIndicatorList(qotGetMacroIndicatorList)`


* **介绍**

    协议请求与返回定义

* **参数**

```protobuf
// 宏观数据国家/地区
enum MacroRegion {
    MacroRegion_Unknown = 0; //未知
    MacroRegion_HK = 1;     //香港
    MacroRegion_US = 2;     //美国
    MacroRegion_JP = 3;     //日本
    MacroRegion_SG = 4;     //新加坡
    MacroRegion_AU = 5;     //澳大利亚
    MacroRegion_CA = 6;     //加拿大
    MacroRegion_MY = 7;     //马来西亚
    MacroRegion_CN = 8;     //中国(沪深)
}

// 宏观指标信息
message MacroIndicatorInfo {
    required uint64 indicatorId = 1; //宏观指标ID
    optional string name = 2;        //指标名称
}

// 宏观指标分类
message MacroIndicatorCategory {
    required string categoryName = 1;                  //分类名称(如"全部"/"就业"/"通胀"/"利率")
    repeated MacroIndicatorInfo indicatorList = 2;     //该分类下的宏观指标列表
}

message C2S {
    required int32 region = 1; //MacroRegion, 国家/地区
    optional Qot_Common.QotHeader header = 100; //行情公共参数头
}

message S2C {
    repeated MacroIndicatorCategory indicatorList = 1; //分类指标列表
}

message Request {
    required C2S c2s = 1;
}

message Response {
    required int32 retType = 1 [default = -400]; //RetType,返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3402


* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetMacroIndicatorList(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11111, false, "xxxxxx"];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: { region: 1 },
            };
            websocket.GetMacroIndicatorList(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetMacroIndicatorList: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetMacroIndicatorList()
```

* **Output**

``` JavaScript
GetMacroIndicatorList: errCode 0, retMsg , retType 0
{
  "indicatorList": [
    {
      "categoryName": "物价",
      "indicatorList": [
        { "indicatorId": "1003000003", "name": "美国生产者物价指数(PPI)同比" },
        { "indicatorId": "1003000001", "name": "美国核心CPI同比" },
        { "indicatorId": "1003000002", "name": "美国CPI同比" }
      ]
    }
  ]
}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取宏观指标历史数据

`getMacroIndicatorHistory(qotGetMacroIndicatorHistory)`


* **介绍**

    获取宏观指标历史数据，返回指定宏观指标的历史数据点列表，包含数据日期、公布日期、公布值、预测值、前值等信息，按时间降序排列。

* **参数**

```protobuf
// 宏观数据单位类型
enum MacroDataUnitType {
    MacroDataUnitType_Unknown = 0;   //未知
    MacroDataUnitType_Percent = 1;   //百分比(%)
    MacroDataUnitType_Value = 2;     //数值
    MacroDataUnitType_Index = 3;     //指数
}

// 宏观数据点
message MacroDataPoint {
    optional string dataTime = 1;       //数据日期 "yyyy-MM-dd"
    optional string releaseTime = 2;    //公布日期 "yyyy-MM-dd HH:mm:ss"
    optional double value = 3;          //公布值(已还原为原始值)
    optional double predictValue = 4;   //预测值(已还原)
    optional double previousValue = 5;  //前值(已还原)
    optional int32 unitType = 6;        //MacroDataUnitType, 单位类型
}

message C2S {
    required uint64 indicatorId = 1;  //宏观指标ID(来自Qot_GetMacroIndicatorList返回)
    optional string time = 2;         //时间节点 "yyyy-MM-dd"，从该时间往前拉取；不传默认当前时间
    optional int32 maxCount = 3;      //拉取条数，默认100，上限1000
    optional Qot_Common.QotHeader header = 100; //行情公共参数头
}

message S2C {
    optional uint64 indicatorId = 1;           //指标ID(回显)
    repeated MacroDataPoint dataList = 2;      //历史数据点列表(按时间降序)
}

message Request {
    required C2S c2s = 1;
}

message Response {
    required int32 retType = 1 [default = -400]; //RetType,返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3403


* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetMacroIndicatorHistory(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11111, false, "xxxxxx"];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: { indicatorId: 1003000003 },
            };
            websocket.GetMacroIndicatorHistory(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetMacroIndicatorHistory: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetMacroIndicatorHistory()
```

* **Output**

``` JavaScript
GetMacroIndicatorHistory: errCode 0, retMsg , retType 0
{
  "indicatorId": "1003000003",
  "dataList": [
    { "dataTime": "2026-05-01", "value": 0.0642, "previousValue": 0.0566, "unitType": "PERCENT" },
    { "dataTime": "2026-04-01", "value": 0.0566, "previousValue": 0.0427, "unitType": "PERCENT" },
    { "dataTime": "2026-03-01", "value": 0.0427, "previousValue": 0.0338, "unitType": "PERCENT" }
  ]
}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取FedWatch目标利率概率

`getFedWatchTargetRate(qotGetFedWatchTargetRate)`


* **介绍**

    获取 CME FedWatch 工具的联邦基金目标利率概率预测数据。返回各次 FOMC 会议对应的目标利率区间及市场隐含概率分布，数据来源于 CME 联邦基金期货定价。

* **参数**

```protobuf
// 目标利率概率项
message TargetRateItem {
    required string targetRange = 1;     //目标利率区间，如"4.25% ~ 4.50%"
    required double probability = 2;     //市场预期概率(%)，如92.13表示92.13%
}

// 单次 FOMC 会议预测
message FedMeetingTab {
    required string meetingDate = 1;               //会议日期 "yyyy-MM-dd"
    repeated TargetRateItem targetRateList = 2;    //目标利率概率分布(按利率从低到高排列，概率之和=100%)
}

message C2S {
    optional Qot_Common.QotHeader header = 100; //行情公共参数头
}

message S2C {
    repeated FedMeetingTab meetingList = 1;      //FOMC会议预测列表(按会议日期从近到远排列)
}

message Request {
    required C2S c2s = 1;
}

message Response {
    required int32 retType = 1 [default = -400]; //RetType,返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3404


* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetFedWatchTargetRate(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11111, false, "xxxxxx"];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: {},
            };
            websocket.GetFedWatchTargetRate(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetFedWatchTargetRate: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetFedWatchTargetRate()
```

* **Output**

``` JavaScript
GetFedWatchTargetRate: errCode 0, retMsg , retType 0
{
  "meetingList": [
    {
      "meetingDate": "2026-07-29",
      "tabList": [
        { "targetRange": "3.50-3.75%", "probability": 63.7 },
        { "targetRange": "3.75-4.00%", "probability": 36.3 }
      ]
    },
    {
      "meetingDate": "2026-09-16",
      "tabList": [
        { "targetRange": "3.50-3.75%", "probability": 26.0 },
        { "targetRange": "3.75-4.00%", "probability": 52.5 },
        { "targetRange": "4.00-4.25%", "probability": 21.5 }
      ]
    }
  ]
}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取FedWatch点阵图

`getFedWatchDotPlot(qotGetFedWatchDotPlot)`


* **介绍**

    获取 CME 利率点阵图数据。返回美联储各 FOMC 委员对未来各年份联邦基金利率预期的投票分布，包含每个利率水平的投票人数、中位数利率以及当前联邦基金利率。

* **参数**

```protobuf
// 点阵分组(同一利率水平的投票)
message DotGroup {
    required double rate = 1;        //预期利率(%)，如4.125表示4.125%
    required int32 voteCount = 2;    //投票人数(在该利率水平投票的委员数)
    optional bool isMedian = 3;      //是否为该年份的中位数利率
}

// 单年份点阵数据
message DotPlotYear {
    required int32 year = 1;             //年份，如2025、2026、2027
    repeated DotGroup dotList = 2;       //点阵分布(按利率从低到高排列)
    optional double medianRate = 3;      //该年份中位数利率(%)，便于快速获取
}

message C2S {
    optional Qot_Common.QotHeader header = 100; //行情公共参数头
}

message S2C {
    repeated DotPlotYear yearList = 1;       //按年份从近到远排列的点阵数据
    optional double currentRate = 2;         //当前联邦基金利率(%)，如4.375表示4.375%
}

message Request {
    required C2S c2s = 1;
}

message Response {
    required int32 retType = 1 [default = -400]; //RetType,返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3405


* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetFedWatchDotPlot(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11111, false, "xxxxxx"];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: {},
            };
            websocket.GetFedWatchDotPlot(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetFedWatchDotPlot: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetFedWatchDotPlot()
```

* **Output**

``` JavaScript
GetFedWatchDotPlot: errCode 0, retMsg , retType 0
{
  "currentRate": 3.63,
  "yearList": [
    {
      "year": 2026,
      "currentRate": 3.63,
      "medianRate": 3.875,
      "dotList": [
        { "rate": 3.375, "voteCount": 1, "isMedian": false },
        { "rate": 3.625, "voteCount": 8, "isMedian": false },
        { "rate": 3.875, "voteCount": 3, "isMedian": true },
        { "rate": 4.125, "voteCount": 5, "isMedian": false },
        { "rate": 4.375, "voteCount": 1, "isMedian": false }
      ]
    }
  ]
}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取盈利超预期排名

`getEarningsBeatRank(qotGetEarningsBeatRank)`


* **介绍**

    协议请求与返回定义

* **参数**

```protobuf
// 盈利超预期类型
enum BeatType {
    BeatType_Unknown = 0;
    BeatType_EPS = 1;       // 每股收益
    BeatType_REVENUE = 2;   // 营收
    BeatType_EBIT = 3;      // 息税前利润
}

// 财报周期
enum BeatTerm {
    BeatTerm_Latest = 0;           // 最近一期 (默认)
    BeatTerm_LatestQuarter = 1;    // 最近一期季报
    BeatTerm_LatestHalf = 2;       // 最近一期半年报
    BeatTerm_LatestAnnual = 3;     // 最近一期年报
    BeatTerm_All = 4;              // 全部（时间一样季报优先，时间不同最近一期）
}

// 筛选条件类型
enum IndicatorType {
    IndicatorType_Unknown = 0;
    IndicatorType_BeatRatio = 1;         //【范围】超预期比率
    IndicatorType_ReleasedDate = 2;      //【范围】发布时间(时间戳秒)
    IndicatorType_MarketCap = 3;         //【范围】市值
    IndicatorType_Price = 4;             //【范围】最新价
    IndicatorType_PeTTM = 5;             //【范围】市盈率TTM
}

// 排序字段 (固定降序)
enum SortField {
    SortField_Unknown = 0;               // 默认按市值排序
    SortField_BeatRatio = 1;             // 超预期比率
    SortField_EarningDayChg = 2;         // 财报后首日涨幅
    SortField_ReleasedDate = 3;          // 发布时间
    SortField_Actual = 4;               // 实际值
    SortField_Estimate = 5;             // 预测值
    SortField_Yoy = 6;                  // 去年同期
    SortField_YoyGrowth = 7;            // 同比增长率
    SortField_PeTTM = 8;               // 市盈率TTM
    SortField_DividendsTTM = 9;         // 股息率TTM
    SortField_Price = 10;               // 价格
    SortField_ChangeRate = 11;          // 今日涨跌幅
}

// 财报发布时段
enum PostPeriodType {
    PostPeriodType_Regular = 0;          // 当天(未识别出时段)
    PostPeriodType_Before = 1;           // 盘前
    PostPeriodType_After = 2;            // 盘后
    PostPeriodType_IntradayTrading = 3;  // 盘中
}

// 筛选条件
message Indicator {
    required int32 indicatorType = 1;                   // IndicatorType
    optional Qot_OptionCommon.Interval indicatorValue = 2;  // 筛选区间
}

message C2S {
    required int32 market = 1;          // Qot_Common.QotMarket (仅支持 HK=1, US=11, SG=31, JP=41)
    required int32 beatType = 2;        // BeatType
    optional int32 count = 3;           // 返回数量 [1,300], 默认30
    optional int32 term = 4;            // BeatTerm, 默认 All
    repeated Indicator filterList = 5;  // 可选筛选条件(AND关系), 不传则使用默认值(超预期>0, 时间=最近30天)
    optional int32 sortField = 6;       // SortField, 排序字段(固定降序), 默认按市值
}

// 盈利超预期排行数据项
message EarningsBeatItem {
    required Qot_Common.Security security = 1;  // 股票
    optional string name = 2;                    // 名称
    optional string industry = 3;               // 行业

    // 行情
    optional double curPrice = 10;              // 最新价
    optional double lastClosePrice = 11;        // 昨收价
    optional double changeRate = 12;            // 今日涨跌幅 (%)
    optional double marketCap = 13;             // 市值
    optional double peTTM = 14;                 // 市盈率TTM
    optional double dividendsTTM = 15;          // 股息率TTM (%)

    // 盈利超预期
    optional string releasedDate = 20;          // 发布日期 (如 "2024-01-15")
    optional double beatRatio = 21;             // 超预期比率 (%)
    optional double actual = 22;                // 实际值
    optional double estimate = 23;              // 预测值
    optional double yoy = 24;                   // 去年同期
    optional double yoyGrowth = 25;             // 同比增长率 (%)
    optional double earningDayChg = 26;         // 财报后首日涨幅 (%)
    optional string term = 27;                  // 财报周期 (如 "2024/Q1")
    optional int32 detailPostPeriod = 28;       // PostPeriodType, 发布具体时段
}

message S2C {
    repeated EarningsBeatItem dataList = 1;     // 数据列表
    optional int32 allCount = 2;                // 数据总量
}

message Request {
    required C2S c2s = 1;
}

message Response {
    required int32 retType = 1 [default = -400]; // RetType, 返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3406


* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetEarningsBeatRank(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11111, false, "xxxxxx"];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: { market: 11, beatType: 1, count: 3 },
            };
            websocket.GetEarningsBeatRank(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetEarningsBeatRank: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetEarningsBeatRank()
```

* **Output**

``` JavaScript
GetEarningsBeatRank: errCode 0, retMsg , retType 0
{
  "allCount": 1282,
  "dataList": [
    { "security": { "market": 11, "code": "NVDA" }, "name": "英伟达", "beatRatio": 37.253, "earningDayChg": -1.772 },
    { "security": { "market": 11, "code": "GOOGL" }, "name": "谷歌-A", "beatRatio": 91.593, "earningDayChg": 9.961 },
    { "security": { "market": 11, "code": "GOOG" }, "name": "谷歌-C", "beatRatio": 91.593, "earningDayChg": 9.970 }
  ]
}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取股息排行

`getDividendRank(qotGetDividendRank)`


* **介绍**

    协议请求与返回定义

* **参数**

```protobuf
// 股息排行类型
enum DividendRankType {
    DividendRankType_Unknown = 0;
    DividendRankType_HighYield = 1;      // 高股息率
    DividendRankType_DividendGrowth = 2; // 股息保持增长
}

// 筛选条件类型
enum IndicatorType {
    IndicatorType_Unknown = 0;
    IndicatorType_DividendYieldTTM = 1;       //【范围】股息率TTM (%)
    IndicatorType_AvgDividendYield5Y = 2;     //【范围】5年平均股息率 (%)
    IndicatorType_DistributionFrequency = 3;  //【枚举】派息频率 (1:年派, 2:半年派, 3:季派, 4:月派)
    IndicatorType_DividendGrowYear = 4;       //【范围】股息连续增长年数
    IndicatorType_DividendsTTM = 5;           //【范围】股息TTM (金额)
    IndicatorType_PayoutRatioLFY = 6;         //【范围】股息支付率LFY (%)
    IndicatorType_NextPayableDate = 7;        //【范围】下次派息日 (相对天数)
    IndicatorType_Price = 8;                  //【范围】最新价
    IndicatorType_MarketCap = 9;              //【范围】市值
}

// 排序字段 (固定降序)
enum SortField {
    SortField_Unknown = 0;               // 默认: HighYield→股息率TTM, DividendGrowth→连续增长年数
    SortField_DividendYieldTTM = 1;      // 股息率TTM
    SortField_AvgDividendYield5Y = 2;    // 5年平均股息率
    SortField_DistributionFrequency = 3; // 派息频率
    SortField_DividendGrowYear = 4;      // 股息连续增长年数
    SortField_DividendsTTM = 5;          // 股息TTM
    SortField_PayoutRatioLFY = 6;        // 股息支付率LFY
    SortField_Price = 7;                 // 价格
    SortField_MarketCap = 8;             // 市值
    SortField_ChangeRate = 9;            // 今日涨跌幅
    SortField_ChangeAmount = 10;         // 今日涨跌额
}

// 筛选条件
message Indicator {
    required int32 indicatorType = 1;                              // IndicatorType
    optional Qot_OptionCommon.IndicatorValue indicatorValue = 2;   // 筛选值(枚举型用valueList, 范围型用valueInterval)
}

message C2S {
    required int32 market = 1;              // Qot_Common.QotMarket (仅支持 HK=1, US=11, MY=61, SG=31, JP=41)
    required int32 rankType = 2;            // DividendRankType
    optional int32 count = 3;               // 返回数量 [1,300], 默认10
    repeated Indicator filterList = 4;      // 可选筛选条件(AND关系)
    optional int32 sortField = 5;           // SortField, 排序字段(固定降序), 默认由rankType决定
}

// 股息排行数据项
message DividendRankItem {
    required Qot_Common.Security security = 1;  // 股票
    optional string name = 2;                    // 名称
    optional string industry = 3;               // 行业

    // 行情
    optional double curPrice = 10;              // 最新价
    optional double changeRate = 11;            // 今日涨跌幅 (%)
    optional double changeAmount = 12;          // 今日涨跌额
    optional double marketCap = 13;             // 市值

    // 股息
    optional double dividendYieldTTM = 20;      // 股息率TTM (%)
    optional double avgDividendYield5Y = 21;    // 5年平均股息率 (%)
    optional int32 distributionFrequency = 22;  // 派息频率 (1:年派, 2:半年派, 3:季派, 4:月派)，不支持HK市场
    optional int32 dividendGrowYear = 23;       // 股息连续增长年数
    optional double dividendsTTM = 24;          // 股息TTM (金额)
    optional double payoutRatioLFY = 25;        // 股息支付率LFY (%)
    optional string nextPayableDate = 26;       // 下次派息日 ("YYYY-MM-DD")
}

message S2C {
    repeated DividendRankItem dataList = 1;     // 数据列表
}

message Request {
    required C2S c2s = 1;
}

message Response {
    required int32 retType = 1 [default = -400]; // RetType, 返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3407


* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetDividendRank(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11111, false, "xxxxxx"];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: { market: 1, rankType: 1, count: 3 },
            };
            websocket.GetDividendRank(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetDividendRank: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetDividendRank()
```

* **Output**

``` JavaScript
GetDividendRank: errCode 0, retMsg , retType 0
{
  "dataList": [
    { "security": { "market": 1, "code": "00288" }, "name": "万洲国际", "dividendYieldTtm": 10.569, "dividendsTtm": 0.910 },
    { "security": { "market": 1, "code": "01919" }, "name": "中远海控", "dividendYieldTtm": 8.302, "dividendsTtm": 1.125 },
    { "security": { "market": 1, "code": "01088" }, "name": "中国神华", "dividendYieldTtm": 7.578, "dividendsTtm": 3.227 }
  ]
}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取派息日历

`getDividendCalendar(qotGetDividendCalendar)`


* **介绍**

    获取派息日历，返回指定市场中某一天的派息数据列表，包含除净日、股权登记日、派息日等信息。

* **参数**

```protobuf
message C2S {
    required int32 market = 1;          // Qot_Common.QotMarket (支持 HK=1, US=11, MY=61, SG=31, JP=41)
    required string date = 2;           // 查询日期, 格式"YYYY-MM-DD"
    optional int32 dataFrom = 3;        // 分页偏移量, 默认0
    optional int32 count = 4;           // 返回数量, 默认不限
}

// 派息日历单条记录
message DividendCalendarItem {
    required Qot_Common.Security security = 1;      // 股票
    optional string name = 2;                        // 股票名称
    optional string statement = 3;                   // 方案说明
    optional string recordDate = 4;                  // 股权登记日 ("YYYY-MM-DD")
    optional string exDate = 5;                      // 除净日 ("YYYY-MM-DD")
    optional string dividendPayableDate = 6;         // 派息日 ("YYYY-MM-DD")
}

message S2C {
    repeated DividendCalendarItem itemList = 1;      // 派息列表
    optional int32 allCount = 2;                     // 该日期下的总数量
}

message Request {
    required C2S c2s = 1;
}

message Response {
    required int32 retType = 1 [default = -400]; // RetType, 返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3408


* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetDividendCalendar(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11111, false, "xxxxxx"];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: {
                    market: 11, // Qot_Common.QotMarket_US
                    date: "2026-06-23",
                    count: 3,
                },
            };
            websocket.GetDividendCalendar(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetDividendCalendar: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetDividendCalendar()
```

* **Output**

``` JavaScript
GetDividendCalendar: errCode 0, retMsg , retType 0
{
  "allCount": 85,
  "itemList": [
    { "security": { "market": 11, "code": "APH" }, "name": "安费诺", "statement": "1股派息0.25USD", "exDate": "2026-06-23" },
    { "security": { "market": 11, "code": "SATA" }, "name": "STRIVE INC PERP PFD SER A VAR RATE", "statement": "1股派息0.0542USD", "exDate": "2026-06-23" },
    { "security": { "market": 11, "code": "CNQ" }, "name": "加拿大自然资源", "statement": "1股派息0.46618USD", "exDate": "2026-06-23" }
  ]
}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取经济事件日历

`getEconomicCalendar(qotGetEconomicCalendar)`


* **介绍**

    协议请求与返回定义

* **参数**

```protobuf
// 事件重要性(星级)
enum Importance {
    Importance_All = 0;       //全部(默认)
    Importance_Low = 1;       //一星(低)
    Importance_Medium = 2;    //二星(中)
    Importance_High = 3;      //三星(高)
}

// 经济数据事件
message EconomicCalendarItem {
    optional string title = 1;          // 标题(如"非农就业人数")
    optional double timestamp = 2;      // 发布时间戳(秒)
    optional string country = 3;        // 国家名称
    optional int32 star = 4;            // 星级(重要性 1-3)
    optional string previous = 5;       // 前值
    optional string consensus = 6;      // 预测值
    optional string actual = 7;         // 实际值(公布值)
}

message C2S {
    required string beginDate = 1;      // 开始日期，格式"yyyy-MM-dd"，按本机系统时区解释
    optional string endDate = 2;        // 结束日期，格式"yyyy-MM-dd"，不传则仅查beginDate当天
    repeated int32 marketList = 3;      // Qot_Common.QotMarket，市场筛选(多选，支持HK/US/CNSH/SG/JP/AU/MY/CA)
    optional int32 importance = 4;      // Importance，事件重要性筛选，默认All
    optional int32 count = 5;           // 每页数量，默认50，最大100
    optional string nextPage = 6;       // 翻页标记，首次不传，后续带上S2C返回的nextPage
}

message S2C {
    repeated EconomicCalendarItem itemList = 1; // 经济数据事件列表
    optional string nextPage = 2;               // 下一页翻页标记
    optional bool hasMore = 3;                  // 是否还有更多数据
}

message Request {
    required C2S c2s = 1;
}

message Response {
    required int32 retType = 1 [default = -400]; //RetType，返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3409


* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetEconomicCalendar(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11111, false, "xxxxxx"];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: {
                    beginDate: "2026-06-22",
                    endDate: "2026-06-22",
                    count: 3,
                },
            };
            websocket.GetEconomicCalendar(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetEconomicCalendar: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetEconomicCalendar()
```

* **Output**

``` JavaScript
GetEconomicCalendar: errCode 0, retMsg , retType 0
{
  "hasMore": false,
  "itemList": [
    { "title": "中国至6月22日一年期贷款市场报价利率", "timestamp": 1782090000, "country": "中国", "star": "HIGH" },
    { "title": "中国至6月22日五年期贷款市场报价利率", "timestamp": 1782090000, "country": "中国", "star": "MEDIUM" },
    { "title": "美国至6月22日6个月国债竞拍-投标倍数", "timestamp": 1782142000, "country": "美国", "star": "LOW" }
  ]
}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取盘前榜

`getUSPreMarketRank(qotGetUSPreMarketRank)`


* **介绍**

    协议请求与返回定义

* **参数**

```protobuf
// 排序方向
enum SortDir {
    SortDir_Descending = 0;     // 降序(领涨,默认)
    SortDir_Ascending = 1;      // 升序(领跌)
}

// 筛选条件类型
enum IndicatorType {
    IndicatorType_Unknown = 0;
    IndicatorType_Price = 1;           // 价格筛选(枚举, 参考PriceFilter)
    IndicatorType_MarketCap = 2;       // 市值区间
    IndicatorType_PE = 3;              // 市盈率区间
}

// 价格筛选枚举
enum PriceFilter {
    PriceFilter_All = 0;              // 所有(默认)
    PriceFilter_LessThan1 = 1;        // 小于1
    PriceFilter_Between1And10 = 2;    // 1~10之间
    PriceFilter_Between10And100 = 3;  // 10~100之间
    PriceFilter_GreaterThan100 = 4;   // 大于100
    PriceFilter_Near52WeekHigh = 5;   // 接近52周最高
    PriceFilter_Near52WeekLow = 6;    // 接近52周最低
}

// 筛选条件
message Indicator {
    required int32 indicatorType = 1;                       // IndicatorType
    optional Qot_OptionCommon.Interval indicatorValue = 2;  // 筛选区间(MarketCap/PE使用)
    optional int32 priceFilter = 3;                         // PriceFilter, 价格筛选枚举(IndicatorType_Price时使用)
}

message C2S {
    optional int32 sortDir = 1;            // SortDir, 排序方向, 默认降序(领涨)
    optional int32 offset = 2;             // 起始位置, 默认0
    optional int32 count = 3;              // 返回数量 [1,200], 默认50
    repeated Indicator filterList = 4;     // 筛选条件(AND关系)
}

// 盘前榜数据项
message PreMarketRankItem {
    required Qot_Common.Security security = 1;  // 股票
    optional string name = 2;                    // 名称

    optional double preMarketPrice = 10;          // 盘前价
    optional double preMarketChangeRatio = 11;    // 盘前涨跌幅(%)
    optional double preMarketChangeAmount = 12;   // 盘前涨跌额
    optional double preMarketTurnover = 13;       // 盘前成交额
    optional int64 preMarketVolume = 14;          // 盘前成交量
    optional double closePrice = 15;              // 收盘价(上一交易日)
    optional double changeRatio = 16;             // 盘中涨跌幅(%)
    optional double changeAmount = 17;            // 盘中涨跌额
}

message S2C {
    repeated PreMarketRankItem dataList = 1;    // 数据列表
    optional int32 allCount = 2;                // 符合条件的总数据量
}

message Request {
    required C2S c2s = 1;
}

message Response {
    required int32 retType = 1 [default = -400]; // RetType, 返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3410


* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetUSPreMarketRank(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11111, false, "xxxxxx"];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: { count: 3 },
            };
            websocket.GetUSPreMarketRank(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetUSPreMarketRank: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetUSPreMarketRank()
```

* **Output**

``` JavaScript
GetUSPreMarketRank: errCode 0, retMsg , retType 0
{
  "allCount": 17711,
  "dataList": [
    { "security": { "market": 11, "code": "GETY" }, "name": "Getty Images", "preMarketPrice": 1.639, "preMarketChangeRatio": 170.996 },
    { "security": { "market": 11, "code": "ADTX" }, "name": "Aditxt", "preMarketPrice": 0.020, "preMarketChangeRatio": 109.000 },
    { "security": { "market": 11, "code": "EHGO" }, "name": "君长数码", "preMarketPrice": 3.270, "preMarketChangeRatio": 81.672 }
  ]
}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取盘后榜

`getUSAfterHoursRank(qotGetUSAfterHoursRank)`


* **介绍**

    协议请求与返回定义

* **参数**

```protobuf
// 排序方向
enum SortDir {
    SortDir_Descending = 0;     // 降序(领涨,默认)
    SortDir_Ascending = 1;      // 升序(领跌)
}

// 筛选条件类型
enum IndicatorType {
    IndicatorType_Unknown = 0;
    IndicatorType_Price = 1;           // 价格筛选(枚举, 参考PriceFilter)
    IndicatorType_MarketCap = 2;       // 市值区间
    IndicatorType_PE = 3;              // 市盈率区间
}

// 价格筛选枚举
enum PriceFilter {
    PriceFilter_All = 0;              // 所有(默认)
    PriceFilter_LessThan1 = 1;        // 小于1
    PriceFilter_Between1And10 = 2;    // 1~10之间
    PriceFilter_Between10And100 = 3;  // 10~100之间
    PriceFilter_GreaterThan100 = 4;   // 大于100
    PriceFilter_Near52WeekHigh = 5;   // 接近52周最高
    PriceFilter_Near52WeekLow = 6;    // 接近52周最低
}

// 筛选条件
message Indicator {
    required int32 indicatorType = 1;                       // IndicatorType
    optional Qot_OptionCommon.Interval indicatorValue = 2;  // 筛选区间(MarketCap/PE使用)
    optional int32 priceFilter = 3;                         // PriceFilter, 价格筛选枚举(IndicatorType_Price时使用)
}

message C2S {
    optional int32 sortDir = 1;            // SortDir, 排序方向, 默认降序(领涨)
    optional int32 offset = 2;             // 起始位置, 默认0
    optional int32 count = 3;              // 返回数量 [1,200], 默认50
    repeated Indicator filterList = 4;     // 筛选条件(AND关系)
}

// 盘后榜数据项
message AfterHoursRankItem {
    required Qot_Common.Security security = 1;  // 股票
    optional string name = 2;                    // 名称

    optional double afterHoursPrice = 10;          // 盘后价
    optional double afterHoursChangeRatio = 11;    // 盘后涨跌幅(%)
    optional double afterHoursChangeAmount = 12;   // 盘后涨跌额
    optional double afterHoursTurnover = 13;       // 盘后成交额
    optional int64 afterHoursVolume = 14;          // 盘后成交量
    optional double closePrice = 15;               // 收盘价(上一交易日)
    optional double changeRatio = 16;              // 盘中涨跌幅(%)
    optional double changeAmount = 17;             // 盘中涨跌额
}

message S2C {
    repeated AfterHoursRankItem dataList = 1;   // 数据列表
    optional int32 allCount = 2;                // 符合条件的总数据量
}

message Request {
    required C2S c2s = 1;
}

message Response {
    required int32 retType = 1 [default = -400]; // RetType, 返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3411


* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetUSAfterHoursRank(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11111, false, "xxxxxx"];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: { count: 3 },
            };
            websocket.GetUSAfterHoursRank(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetUSAfterHoursRank: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetUSAfterHoursRank()
```

* **Output**

``` JavaScript
GetUSAfterHoursRank: errCode 0, retMsg , retType 0
{
  "allCount": 17711,
  "dataList": [
    { "security": { "market": 11, "code": "TNON" }, "name": "Tenon Medical", "afterHoursPrice": 0.640, "afterHoursChangeRatio": 82.857 },
    { "security": { "market": 11, "code": "SAGT" }, "name": "Sagtec Global", "afterHoursPrice": 1.806, "afterHoursChangeRatio": 82.434 },
    { "security": { "market": 11, "code": "CANG" }, "name": "灿谷", "afterHoursPrice": 0.280, "afterHoursChangeRatio": 47.421 }
  ]
}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取夜盘榜

`getUSOvernightRank(qotGetUSOvernightRank)`


* **介绍**

    协议请求与返回定义

* **参数**

```protobuf
// 排序方向
enum SortDir {
    SortDir_Descending = 0;     // 降序(领涨,默认)
    SortDir_Ascending = 1;      // 升序(领跌)
}

// 筛选条件类型
enum IndicatorType {
    IndicatorType_Unknown = 0;
    IndicatorType_Price = 1;           // 价格筛选(枚举, 参考PriceFilter)
    IndicatorType_MarketCap = 2;       // 市值区间
    IndicatorType_PE = 3;              // 市盈率区间
}

// 价格筛选枚举
enum PriceFilter {
    PriceFilter_All = 0;              // 所有(默认)
    PriceFilter_LessThan1 = 1;        // 小于1
    PriceFilter_Between1And10 = 2;    // 1~10之间
    PriceFilter_Between10And100 = 3;  // 10~100之间
    PriceFilter_GreaterThan100 = 4;   // 大于100
    PriceFilter_Near52WeekHigh = 5;   // 接近52周最高
    PriceFilter_Near52WeekLow = 6;    // 接近52周最低
}

// 筛选条件
message Indicator {
    required int32 indicatorType = 1;                       // IndicatorType
    optional Qot_OptionCommon.Interval indicatorValue = 2;  // 筛选区间(MarketCap/PE使用)
    optional int32 priceFilter = 3;                         // PriceFilter, 价格筛选枚举(IndicatorType_Price时使用)
}

message C2S {
    optional int32 sortDir = 1;            // SortDir, 排序方向, 默认降序(领涨)
    optional int32 offset = 2;             // 起始位置, 默认0
    optional int32 count = 3;              // 返回数量 [1,200], 默认50
    repeated Indicator filterList = 4;     // 筛选条件(AND关系)
}

// 夜盘榜数据项
message OvernightRankItem {
    required Qot_Common.Security security = 1;  // 股票
    optional string name = 2;                    // 名称

    optional double overnightPrice = 10;           // 夜盘价
    optional double overnightChangeRatio = 11;     // 夜盘涨跌幅(%)
    optional double overnightChangeAmount = 12;    // 夜盘涨跌额
    optional double overnightTurnover = 13;        // 夜盘成交额
    optional int64 overnightVolume = 14;           // 夜盘成交量
    optional double closePrice = 15;               // 收盘价(上一交易日)
    optional double changeRatio = 16;              // 盘中涨跌幅(%)
    optional double changeAmount = 17;             // 盘中涨跌额
}

message S2C {
    repeated OvernightRankItem dataList = 1;    // 数据列表
    optional int32 allCount = 2;                // 符合条件的总数据量
}

message Request {
    required C2S c2s = 1;
}

message Response {
    required int32 retType = 1 [default = -400]; // RetType, 返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3412


* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetUSOvernightRank(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11111, false, "xxxxxx"];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: { count: 3 },
            };
            websocket.GetUSOvernightRank(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetUSOvernightRank: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetUSOvernightRank()
```

* **Output**

``` JavaScript
GetUSOvernightRank: errCode 0, retMsg , retType 0
{
  "allCount": 17711,
  "dataList": [
    { "security": { "market": 11, "code": "TNON" }, "name": "Tenon Medical", "overnightPrice": 0.7310, "overnightChangeRatio": 108.857 },
    { "security": { "market": 11, "code": "SAGT" }, "name": "Sagtec Global", "overnightPrice": 2.0500, "overnightChangeRatio": 107.070 },
    { "security": { "market": 11, "code": "CANG" }, "name": "灿谷", "overnightPrice": 0.3212, "overnightChangeRatio": 69.052 }
  ]
}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取领涨领跌榜

`getTopMoversRank(qotGetTopMoversRank)`


* **介绍**

    协议请求与返回定义

* **参数**

```protobuf
// 排序方向
enum SortDir {
    SortDir_Descending = 0;     // 降序(领涨,默认)
    SortDir_Ascending = 1;      // 升序(领跌)
}

// 筛选条件类型
enum IndicatorType {
    IndicatorType_Unknown = 0;
    IndicatorType_Price = 1;           // 价格筛选(枚举, 参考PriceFilter)
    IndicatorType_MarketCap = 2;       // 市值区间
    IndicatorType_PE = 3;              // 市盈率区间
}

// 价格筛选枚举
enum PriceFilter {
    PriceFilter_All = 0;              // 所有(默认)
    PriceFilter_LessThan1 = 1;        // 小于1
    PriceFilter_Between1And10 = 2;    // 1~10之间
    PriceFilter_Between10And100 = 3;  // 10~100之间
    PriceFilter_GreaterThan100 = 4;   // 大于100
    PriceFilter_Near52WeekHigh = 5;   // 接近52周最高
    PriceFilter_Near52WeekLow = 6;    // 接近52周最低
}

// 筛选条件
message Indicator {
    required int32 indicatorType = 1;                       // IndicatorType
    optional Qot_OptionCommon.Interval indicatorValue = 2;  // 筛选区间(MarketCap/PE使用)
    optional int32 priceFilter = 3;                         // PriceFilter, 价格筛选枚举(IndicatorType_Price时使用)
}

message C2S {
    required int32 market = 1;             // Qot_Common.QotMarket (HK=1, US=11)
    optional int32 sortDir = 2;            // SortDir, 排序方向, 默认降序(领涨)
    optional int32 offset = 3;             // 起始位置, 默认0
    optional int32 count = 4;              // 返回数量 [1,200], 默认50
    repeated Indicator filterList = 5;     // 筛选条件(AND关系)
}

// 盘中领涨/领跌数据项
message TopMoversRankItem {
    required Qot_Common.Security security = 1;  // 股票
    optional string name = 2;                    // 名称

    optional double curPrice = 10;             // 最新价
    optional double changeRatio = 11;          // 涨跌幅(%)
    optional double changeAmount = 12;         // 涨跌额
    optional double turnover = 13;             // 成交额
    optional int64 volume = 14;                // 成交量
    optional double turnoverRatio = 15;        // 换手率(%)
    optional double peTTM = 16;                // 市盈率TTM
    optional double amplitude = 17;            // 振幅(%)
    optional double marketCap = 18;            // 市值
    optional double volumeRatio = 19;          // 量比
}

message S2C {
    repeated TopMoversRankItem dataList = 1;    // 数据列表
    optional int32 allCount = 2;                // 符合条件的总数据量
}

message Request {
    required C2S c2s = 1;
}

message Response {
    required int32 retType = 1 [default = -400]; // RetType, 返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3413


* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetTopMoversRank(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11111, false, "xxxxxx"];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: { market: 11, count: 3 },
            };
            websocket.GetTopMoversRank(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetTopMoversRank: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetTopMoversRank()
```

* **Output**

``` JavaScript
GetTopMoversRank: errCode 0, retMsg , retType 0
{
  "allCount": 17711,
  "dataList": [
    { "security": { "market": 11, "code": "GRFXY" }, "name": "Graphex Group Ltd", "curPrice": 0.108 },
    { "security": { "market": 11, "code": "CBNT" }, "name": "C-BOND SYSTEMS INC", "curPrice": 0.000 },
    { "security": { "market": 11, "code": "VAXX" }, "name": "Vaxxinity", "curPrice": 0.015 }
  ]
}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取热议榜

`getHotList(qotGetHotList)`


* **介绍**

    协议请求与返回定义

* **参数**

```protobuf
// 排序方向
enum SortDir {
    SortDir_Descending = 0;     // 降序(默认)
    SortDir_Ascending = 1;      // 升序
}

// 排序字段
enum HotListSortField {
    HotListSortField_Unknown = 0;       // 默认(综合热度)
    HotListSortField_TradeHeat = 1;     // 交易热度
    HotListSortField_SearchHeat = 2;    // 搜索热度
    HotListSortField_NewsHeat = 3;      // 资讯热度
    HotListSortField_AverageHeat = 4;   // 综合热度
}

// 筛选条件类型
enum IndicatorType {
    IndicatorType_Unknown = 0;
    IndicatorType_MarketCap = 1;        // 市值区间
}

// 筛选条件
message Indicator {
    required int32 indicatorType = 1;                       // IndicatorType
    optional Qot_OptionCommon.Interval indicatorValue = 2;  // 筛选区间
}

message C2S {
    required int32 market = 1;             // Qot_Common.QotMarket (HK=1, US=11)
    optional int32 sortField = 2;          // HotListSortField, 排序字段, 默认综合热度
    optional int32 sortDir = 3;            // SortDir, 排序方向, 默认降序
    optional int32 offset = 4;             // 起始位置, 默认0
    optional int32 count = 5;              // 返回数量 [1,200], 默认50
    repeated Indicator filterList = 6;     // 筛选条件(市值)
}

// 热议新闻信息
message HotNewsInfo {
    optional int32 newsType = 1;        // 1=社区讨论, 2=资讯
    optional string title = 2;          // 讨论/资讯标题
    optional string newsUrl = 3;        // 资讯URL(newsType=2时有效)
}

// 热议榜数据项
message HotListItem {
    required Qot_Common.Security security = 1;  // 股票
    optional string name = 2;                    // 名称

    optional double tradeHeat = 12;             // 交易热度
    optional double tradeHeatChange = 13;       // 交易热度变化
    optional double searchHeat = 14;            // 搜索热度
    optional double searchHeatChange = 15;      // 搜索热度变化
    optional double newsHeat = 16;              // 资讯热度
    optional double newsHeatChange = 17;        // 资讯热度变化
    optional double averageHeat = 18;           // 综合热度
    optional double averageHeatChange = 19;     // 综合热度变化
    optional HotNewsInfo newsInfo = 20;         // 关联新闻
}

message S2C {
    repeated HotListItem dataList = 1;         // 数据列表
    optional int32 allCount = 2;               // 符合条件的总数据量
}

message Request {
    required C2S c2s = 1;
}

message Response {
    required int32 retType = 1 [default = -400]; // RetType, 返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3414


* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetHotList(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11111, false, "xxxxxx"];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: { market: 11, count: 3 },
            };
            websocket.GetHotList(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetHotList: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetHotList()
```

* **Output**

``` JavaScript
GetHotList: errCode 0, retMsg , retType 0
{
  "allCount": 4822,
  "dataList": [
    { "security": { "market": 11, "code": "SPCX" }, "name": "SpaceX", "averageHeat": 9999954.0 },
    { "security": { "market": 11, "code": "MU" }, "name": "美光科技", "averageHeat": 5554652.0 },
    { "security": { "market": 11, "code": "INTC" }, "name": "英特尔", "averageHeat": 4650380.0 }
  ]
}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取卖空异动榜

`getShortSellingRank(qotGetShortSellingRank)`


* **介绍**

    协议请求与返回定义

* **参数**

```protobuf
// 排序方向
enum SortDir {
    SortDir_Descending = 0;     // 降序(默认)
    SortDir_Ascending = 1;      // 升序
}

// 排序字段
enum ShortSellingSortField {
    ShortSellingSortField_Unknown = 0;                  // 默认(卖空变化量)
    ShortSellingSortField_ShortNumberChange = 1;        // 卖空变化量
    ShortSellingSortField_ShortRatioChange = 2;         // 卖空变化比例
    ShortSellingSortField_ShortNumber = 3;              // 卖空数量
    ShortSellingSortField_ShortRatio = 4;               // 卖空比例
    ShortSellingSortField_Volume = 5;                   // 成交量
    ShortSellingSortField_PositionVolume = 6;           // 空头持仓数量
    ShortSellingSortField_PositionRatio = 7;            // 空头持仓比例
    ShortSellingSortField_DaysToCover = 8;              // 回补天数
    ShortSellingSortField_WeekAvgVolume = 9;            // 近一周日均成交量
    ShortSellingSortField_WeekAvgShortNumber = 10;      // 近一周日均卖空数量
    ShortSellingSortField_WeekAvgShortRatio = 11;       // 近一周日均卖空比例
    ShortSellingSortField_MonthAvgVolume = 12;          // 近一月日均成交量
    ShortSellingSortField_MonthAvgShortNumber = 13;     // 近一月日均卖空数量
    ShortSellingSortField_MonthAvgShortRatio = 14;      // 近一月日均卖空比例
}

message C2S {
    optional int32 market = 1;             // Qot_Common.QotMarket, 市场(HK=1, US=11), 默认US
    optional int32 sortField = 2;          // ShortSellingSortField, 排序字段, 默认卖空变化量
    optional int32 sortDir = 3;            // SortDir, 排序方向, 默认降序
    optional int32 offset = 4;             // 起始位置, 默认0
    optional int32 count = 5;              // 返回数量 [1,35], 默认10
    repeated Qot_Common.Security plateList = 6;  // 行业板块列表, 空=全部
}

// 卖空异动数据项
message ShortSellingRankItem {
    required Qot_Common.Security security = 1;  // 股票
    optional string name = 2;                    // 名称

    optional double closePrice = 10;               // 收盘价
    optional double changeRatio = 11;              // 涨跌幅(%)
    optional double changeRatio5D = 12;            // 5日涨跌幅(%)
    optional double changeRatio10D = 13;           // 10日涨跌幅(%)
    optional int64 volume = 14;                    // 成交量

    optional int64 shortNumber = 20;               // 卖空数量
    optional int64 shortNumberChange = 21;         // 卖空变化量
    optional double shortRatio = 22;               // 卖空比例(%)
    optional double shortRatioChange = 23;         // 卖空变化比例(%)
    optional int64 shortPositionVolume = 24;       // 空头持仓数量
    optional double shortPositionRatio = 25;       // 空头持仓比例(%)
    optional double daysToCover = 26;              // 回补天数
    optional int64 weekAvgShortNumber = 27;        // 近一周日均卖空
    optional double weekAvgShortRatio = 28;        // 近一周日均卖空比例(%)
    optional int64 monthAvgShortNumber = 29;       // 近一月日均卖空
    optional double monthAvgShortRatio = 30;       // 近一月日均卖空比例(%)
}

message S2C {
    repeated ShortSellingRankItem dataList = 1;  // 数据列表
    optional int32 allCount = 2;                 // 符合条件的总数据量
}

message Request {
    required C2S c2s = 1;
}

message Response {
    required int32 retType = 1 [default = -400]; // RetType, 返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3415


* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetShortSellingRank(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11111, false, "xxxxxx"];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: { market: 11, count: 3 },
            };
            websocket.GetShortSellingRank(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetShortSellingRank: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetShortSellingRank()
```

* **Output**

``` JavaScript
GetShortSellingRank: errCode 0, retMsg , retType 0
{
  "allCount": 3,
  "dataList": [
    { "security": { "market": 11, "code": "ADTX" }, "name": "Aditxt", "shortRatio": 5.42, "shortRatioChange": 62.78 },
    { "security": { "market": 11, "code": "CDE" }, "name": "科尔黛伦矿业", "shortRatio": 39.44, "shortRatioChange": 779.14 },
    { "security": { "market": 11, "code": "PFE" }, "name": "辉瑞", "shortRatio": 31.48, "shortRatioChange": 466.48 }
  ]
}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取区间涨跌幅

`getPeriodChangeRank(qotGetPeriodChangeRank)`


* **介绍**

    协议请求与返回定义

* **参数**

```protobuf
// 排序方向
enum SortDir {
    SortDir_Descending = 0;     // 降序(默认)
    SortDir_Ascending = 1;      // 升序
}

// 排序周期
enum PeriodType {
    PeriodType_Unknown = 0;
    PeriodType_5Min = 1;       // 5分钟(默认)
    PeriodType_1Day = 2;       // 1日
    PeriodType_5Day = 3;       // 5日
    PeriodType_20Day = 4;      // 20日
    PeriodType_60Day = 5;      // 60日
    PeriodType_120Day = 6;     // 120日
    PeriodType_250Day = 7;     // 250日
    PeriodType_YTD = 8;        // 年初至今
}

// 筛选条件类型
enum IndicatorType {
    IndicatorType_Unknown = 0;
    IndicatorType_Price = 1;            // 最新价区间
    IndicatorType_MarketCap = 2;        // 市值区间
    IndicatorType_ChangeRatio = 3;      // 涨跌幅区间(按所选周期)
    IndicatorType_Volume = 4;           // 成交量区间
    IndicatorType_Turnover = 5;         // 成交额区间
    IndicatorType_PE = 6;               // 市盈率TTM区间
    IndicatorType_PB = 7;               // 市净率区间
    IndicatorType_TurnoverRatio = 8;    // 换手率区间
    IndicatorType_VolumeRatio = 9;      // 量比区间
    IndicatorType_Amplitude = 10;       // 振幅区间
}

// 筛选条件
message Indicator {
    required int32 indicatorType = 1;                       // IndicatorType
    optional Qot_OptionCommon.Interval indicatorValue = 2;  // 筛选区间
}

message C2S {
    required int32 market = 1;             // Qot_Common.QotMarket (HK=1, US=11)
    optional int32 periodType = 2;         // PeriodType, 排序周期, 默认5分钟
    optional int32 sortDir = 3;            // SortDir, 排序方向, 默认降序
    optional int32 offset = 4;             // 起始位置, 默认0
    optional int32 count = 5;              // 返回数量 [1,200], 默认50
    repeated Indicator filterList = 6;     // 筛选条件(AND关系)
}

// 区间涨跌幅数据项
message PeriodChangeRankItem {
    required Qot_Common.Security security = 1;  // 股票
    optional string name = 2;                    // 名称

    optional double curPrice = 10;              // 最新价
    optional double changeRatio = 11;           // 今日涨跌幅(%)
    optional double turnover = 12;              // 成交额
    optional int64 volume = 13;                 // 成交量
    optional double marketCap = 14;             // 市值

    optional double changeRate5Min = 20;        // 5分钟涨跌幅(%)
    optional double changeRate5D = 21;          // 5日涨跌幅(%)
    optional double changeRate10D = 22;         // 10日涨跌幅(%)
    optional double changeRate20D = 23;         // 20日涨跌幅(%)
    optional double changeRate60D = 24;         // 60日涨跌幅(%)
    optional double changeRate120D = 25;        // 120日涨跌幅(%)
    optional double changeRate250D = 26;        // 250日涨跌幅(%)
    optional double changeRateYTD = 27;         // 年初至今涨跌幅(%)

    optional double peTTM = 30;                 // 市盈率TTM
    optional double pb = 31;                    // 市净率
    optional double turnoverRatio = 32;         // 换手率(%)
    optional double volumeRatio = 33;           // 量比
    optional double amplitude = 34;             // 振幅(%)
}

message S2C {
    repeated PeriodChangeRankItem dataList = 1;  // 数据列表
    optional int32 allCount = 2;                  // 符合条件的总数据量
}

message Request {
    required C2S c2s = 1;
}

message Response {
    required int32 retType = 1 [default = -400]; // RetType, 返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3416


* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetPeriodChangeRank(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11111, false, "xxxxxx"];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: { market: 11, count: 3 },
            };
            websocket.GetPeriodChangeRank(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetPeriodChangeRank: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetPeriodChangeRank()
```

* **Output**

``` JavaScript
GetPeriodChangeRank: errCode 0, retMsg , retType 0
{
  "allCount": 6429,
  "dataList": [
    { "security": { "market": 11, "code": "PAVM" }, "name": "PAVmed", "curPrice": 5.16, "changeRatio": 3.200 },
    { "security": { "market": 11, "code": "JLHL" }, "name": "巨龙在线", "curPrice": 39.69, "changeRatio": 18.832 },
    { "security": { "market": 11, "code": "DGICB" }, "name": "多尼戈尔股份-B", "curPrice": 22.86, "changeRatio": 21.531 }
  ]
}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取破净高股息国央企

`getHighDividendSOERank(qotGetHighDividendSOERank)`


* **介绍**

    协议请求与返回定义

* **参数**

```protobuf
// 排序方向
enum SortDir {
    SortDir_Descending = 0;     // 降序(默认)
    SortDir_Ascending = 1;      // 升序
}

// 排序字段
enum SortField {
    SortField_Unknown = 0;              // 默认(市值降序)
    SortField_DividendYieldTTM = 1;     // 股息率TTM
    SortField_PB = 2;                   // 市净率
    SortField_PeTTM = 3;                // 市盈率TTM
    SortField_Price = 4;                // 最新价
    SortField_ChangeRatio = 5;          // 今日涨跌幅
    SortField_MarketCap = 6;            // 市值
}

// 筛选条件类型
enum IndicatorType {
    IndicatorType_Unknown = 0;
    IndicatorType_Price = 1;                // 价格区间
    IndicatorType_MarketCap = 2;            // 市值区间
    IndicatorType_PE = 3;                   // 市盈率TTM区间
    IndicatorType_DividendYieldTTM = 4;     // 股息率TTM区间
    IndicatorType_ChangeRatio = 5;          // 涨跌幅区间
}

// 筛选条件
message Indicator {
    required int32 indicatorType = 1;                       // IndicatorType
    optional Qot_OptionCommon.Interval indicatorValue = 2;  // 筛选区间
}

message C2S {
    optional int32 sortField = 1;          // SortField, 排序字段, 默认市值
    optional int32 sortDir = 2;            // SortDir, 排序方向, 默认降序
    optional int32 offset = 3;             // 起始位置, 默认0
    optional int32 count = 4;              // 返回数量 [1,200], 默认50
    repeated Indicator filterList = 5;     // 筛选条件(可覆盖默认PB/股息率条件)
}

// 破净高股息国央企数据项
// 默认固定条件(服务端硬编码): 概念板块=特估国企 + PB<=1 + 股息率TTM>=5% + PE>=0
message HighDividendSOERankItem {
    required Qot_Common.Security security = 1;  // 股票
    optional string name = 2;                    // 名称
    optional string industry = 3;               // 所属行业

    optional double curPrice = 10;              // 最新价
    optional double changeRatio = 11;           // 涨跌幅(%)
    optional double turnover = 12;              // 成交额
    optional int64 volume = 13;                 // 成交量
    optional double marketCap = 14;             // 市值

    optional double peTTM = 20;                 // 市盈率TTM
    optional double pb = 21;                    // 市净率
    optional double dividendYieldTTM = 22;      // 股息率TTM(%)
    optional double turnoverRatio = 23;         // 换手率(%)

    optional double changeRate5D = 30;          // 5日涨幅(%)
    optional double changeRate10D = 31;         // 10日涨幅(%)
    optional double changeRate20D = 32;         // 20日涨幅(%)
    optional double changeRate60D = 33;         // 60日涨幅(%)
    optional double changeRate120D = 34;        // 120日涨幅(%)
    optional double changeRate250D = 35;        // 250日涨幅(%)
}

message S2C {
    repeated HighDividendSOERankItem dataList = 1;  // 数据列表
    optional int32 allCount = 2;                    // 符合条件的总数据量
}

message Request {
    required C2S c2s = 1;
}

message Response {
    required int32 retType = 1 [default = -400]; // RetType, 返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3417


* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetHighDividendSOERank(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11111, false, "xxxxxx"];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: { count: 3 },
            };
            websocket.GetHighDividendSOERank(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetHighDividendSOERank: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetHighDividendSOERank()
```

* **Output**

``` JavaScript
GetHighDividendSOERank: errCode 0, retMsg , retType 0
{
  "allCount": 91,
  "dataList": [
    { "security": { "market": 1, "code": "01398" }, "name": "工商银行", "dividendYieldTtm": 5.087, "peTtm": 5.83050 },
    { "security": { "market": 1, "code": "00857" }, "name": "中国石油股份", "dividendYieldTtm": 5.764, "peTtm": 9.35648 },
    { "security": { "market": 1, "code": "00386" }, "name": "中国石油化工股份", "dividendYieldTtm": 5.432, "peTtm": 12.27138 }
  ]
}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取机构列表

`getInstitutionList(qotGetInstitutionList)`


* **介绍**

    协议请求与返回定义

* **参数**

```protobuf
// 排序字段
enum SortField {
    SortField_Unknown = 0;               // 默认(持仓市值)
    SortField_PositionValue = 1;         // 持仓市值
    SortField_PositionValueChange = 2;   // 增减仓
    SortField_PositionCount = 3;         // 持仓股数
    SortField_PositionCountChange = 4;   // 持仓股数变化
}

// 排序方向
enum SortDir {
    SortDir_Descending = 0;     // 降序(默认)
    SortDir_Ascending = 1;      // 升序
}

message C2S {
    required int32 market = 1;              // Qot_Common.QotMarket
    optional int32 sortField = 2;           // SortField, 默认持仓市值
    optional int32 sortDir = 3;             // SortDir, 默认降序
    optional int32 count = 4;               // 条数 [1,200], 默认20
    optional string page = 5;               // 翻页游标, 首次不传, 续页传S2C返回的nextPage
    optional string namePart = 6;           // 机构名模糊搜索
}

// 机构列表数据项
message InstitutionListItem {
    required int32 institutionId = 1;       // 机构ID
    optional string institutionName = 2;    // 机构名称
    optional double positionValue = 3;      // 持仓市值
    optional double positionValueChange = 4;// 持仓市值变化
    optional int32 positionCount = 5;       // 持仓股票数
    optional int32 positionCountChange = 6; // 持仓股票数变化
    optional string disclosureDate = 7;     // 披露日期(yyyy-MM-dd)
}

message S2C {
    repeated InstitutionListItem dataList = 1;  // 数据列表
    optional int32 allCount = 2;                // 总数
    optional string nextPage = 3;               // 下一页游标, 空=无更多
    optional string currency = 4;               // 币种
}

message Request {
    required C2S c2s = 1;
}

message Response {
    required int32 retType = 1 [default = -400]; // RetType, 返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3418


* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetInstitutionList(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11111, false, "xxxxxx"];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: { market: 11, count: 3 },
            };
            websocket.GetInstitutionList(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetInstitutionList: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetInstitutionList()
```

* **Output**

``` JavaScript
GetInstitutionList: errCode 0, retMsg , retType 0
{
  "allCount": 17031,
  "currency": "USD",
  "dataList": [
    { "institutionId": 403413, "institutionName": "贝莱德", "positionValue": 7040103000000.0 },
    { "institutionId": 1951572549, "institutionName": "Vanguard Capital Management, LLC", "positionValue": 4944657000000.0 },
    { "institutionId": 823170, "institutionName": "道富", "positionValue": 3363354000000.0 }
  ]
}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取机构概况

`getInstitutionProfile(qotGetInstitutionProfile)`


* **介绍**

    获取机构概况，返回指定机构的持仓市值、持仓变动统计、Top10 持股占比等画像数据。

* **参数**

```protobuf
message C2S {
    required int32 market = 1;              // Qot_Common.QotMarket
    required int32 institutionId = 2;       // 机构ID
}

message S2C {
    optional string institutionName = 1;    // 机构名称
    optional string description = 2;        // 机构简介
    optional double positionValue = 3;      // 持仓市值
    optional double lastPositionValue = 4;  // 上期持仓市值
    optional double positionValueChangePct = 5; // 市值变化比例(%)
    optional int64 totalHoldingCount = 6;   // 总持仓数
    optional int64 holdingChangeCount = 7;  // 持仓变动数
    optional int32 newCount = 8;            // 建仓标的数
    optional int32 soldOutCount = 9;        // 清仓标的数
    optional int32 increaseCount = 10;      // 增持标的数
    optional int32 decreaseCount = 11;      // 减持标的数
    optional double top10Pct = 12;          // Top10持股占比(%)
    optional double top10PctChange = 13;    // Top10占比变动(%)
    optional string disclosureDate = 14;    // 披露日期(yyyy-MM-dd)
    optional string currency = 15;          // 币种
}

message Request {
    required C2S c2s = 1;
}

message Response {
    required int32 retType = 1 [default = -400]; // RetType, 返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3419


* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetInstitutionProfile(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11111, false, "xxxxxx"];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: { market: 11, institutionId: 403413 },
            };
            websocket.GetInstitutionProfile(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetInstitutionProfile: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetInstitutionProfile()
```

* **Output**

``` JavaScript
GetInstitutionProfile: errCode 0, retMsg , retType 0
{
  "institutionName": "贝莱德",
  "positionValue": 7040102678527.163,
  "totalHoldingCount": 4443,
  "currency": "USD"
}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取机构持仓行业分布

`getInstitutionDistribution(qotGetInstitutionDistribution)`


* **介绍**

    获取机构持仓行业分布，返回指定机构的持仓按行业分类的市值和占比数据。

* **参数**

```protobuf
message C2S {
    required int32 market = 1;              // Qot_Common.QotMarket
    required int32 institutionId = 2;       // 机构ID
}

// 行业分布数据项
message IndustryDistributionItem {
    optional uint64 industryId = 1;         // 行业ID
    optional string industryName = 2;       // 行业名称
    optional double positionValue = 3;      // 持仓市值
    optional double portfolioPct = 4;       // 行业占比(%)
}

message S2C {
    repeated IndustryDistributionItem dataList = 1; // 数据列表
}

message Request {
    required C2S c2s = 1;
}

message Response {
    required int32 retType = 1 [default = -400]; // RetType, 返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3420


* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetInstitutionDistribution(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11111, false, "xxxxxx"];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: { market: 11, institutionId: 403413 },
            };
            websocket.GetInstitutionDistribution(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetInstitutionDistribution: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetInstitutionDistribution()
```

* **Output**

``` JavaScript
GetInstitutionDistribution: errCode 0, retMsg , retType 0
{
  "dataList": [
    { "industryName": "电子", "positionValue": 1377382444141.795, "portfolioPct": 20.4857 },
    { "industryName": "计算机", "positionValue": 1005127353809.240, "portfolioPct": 14.9492 },
    { "industryName": "医药生物", "positionValue": 621853010218.809, "portfolioPct": 9.2488 }
  ]
}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取机构持仓变动

`getInstitutionHoldingChange(qotGetInstitutionHoldingChange)`


* **介绍**

    协议请求与返回定义

* **参数**

```protobuf
// 持仓变动类型
enum HoldingChangeType {
    HoldingChangeType_Unknown = 0;
    HoldingChangeType_New = 1;          // 建仓
    HoldingChangeType_SoldOut = 2;      // 清仓
    HoldingChangeType_Increase = 3;     // 增仓
    HoldingChangeType_Decrease = 4;     // 减仓
}

// 排序字段
enum SortField {
    SortField_Unknown = 0;              // 默认(变动比例)
    SortField_ChangePct = 1;            // 变动比例
    SortField_ChangeShares = 2;         // 变动股数
    SortField_HoldingDate = 3;          // 持仓时间
}

// 排序方向
enum SortDir {
    SortDir_Descending = 0;     // 降序(默认)
    SortDir_Ascending = 1;      // 升序
}

message C2S {
    required int32 market = 1;              // Qot_Common.QotMarket
    required int32 institutionId = 2;       // 机构ID
    optional int32 changeType = 3;          // HoldingChangeType, 默认建仓
    optional int32 sortField = 4;           // SortField
    optional int32 sortDir = 5;             // SortDir
    optional int32 count = 6;               // 条数 [1,200], 默认20
    optional string page = 7;               // 翻页游标, 首次不传
}

// 持仓变动数据项
message HoldingChangeItem {
    required Qot_Common.Security security = 1;  // 股票
    optional string name = 2;                    // 名称
    optional double portfolioPct = 3;            // 持股比例(%)
    optional int64 changeShares = 4;             // 变动股数
    optional double changePct = 5;               // 变动比例(%)
    optional string holdingDate = 6;             // 持仓时间(yyyy-MM-dd)
    optional string source = 7;                  // 披露来源
}

message S2C {
    repeated HoldingChangeItem dataList = 1;    // 数据列表
    optional int32 allCount = 2;                // 总数
    optional string nextPage = 3;               // 下一页游标, 空=无更多
}

message Request {
    required C2S c2s = 1;
}

message Response {
    required int32 retType = 1 [default = -400]; // RetType, 返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3421


* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetInstitutionHoldingChange(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11111, false, "xxxxxx"];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: { market: 11, institutionId: 403413, count: 3 },
            };
            websocket.GetInstitutionHoldingChange(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetInstitutionHoldingChange: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetInstitutionHoldingChange()
```

* **Output**

``` JavaScript
GetInstitutionHoldingChange: errCode 0, retMsg , retType 0
{
  "allCount": 87,
  "dataList": [
    { "security": { "market": 11, "code": "YSS" }, "name": "York Space Systems", "changeShares": 19012439, "changePct": 14.6594 },
    { "security": { "market": 11, "code": "VSNT" }, "name": "Versant Media", "changeShares": 17356403, "changePct": 12.2661 },
    { "security": { "market": 11, "code": "RNA" }, "name": "Atrium Therapeutics", "changeShares": 1205277, "changePct": 7.0460 }
  ]
}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取机构持股列表

`getInstitutionHoldingList(qotGetInstitutionHoldingList)`


* **介绍**

    协议请求与返回定义

* **参数**

```protobuf
// 持仓变动类型
enum HoldingChangeType {
    HoldingChangeType_Unknown = 0;
    HoldingChangeType_New = 1;          // 建仓
    HoldingChangeType_SoldOut = 2;      // 清仓
    HoldingChangeType_Increase = 3;     // 增仓
    HoldingChangeType_Decrease = 4;     // 减仓
}

// 排序字段
enum SortField {
    SortField_Unknown = 0;              // 默认(持仓市值)
    SortField_HoldingValue = 1;         // 持仓市值
    SortField_HoldingPct = 2;           // 持股比例(占股票总市值)
    SortField_LastHoldingPct = 3;       // 上期持股比例
    SortField_ChangeShares = 4;         // 变动股数
    SortField_ChangePct = 5;            // 变动比例
    SortField_PortfolioPct = 6;         // 占机构总仓位比例
    SortField_Industry = 7;             // 行业
    SortField_HoldingDate = 8;          // 持仓时间
}

// 排序方向
enum SortDir {
    SortDir_Descending = 0;     // 降序(默认)
    SortDir_Ascending = 1;      // 升序
}

message C2S {
    required int32 market = 1;              // Qot_Common.QotMarket
    required int32 institutionId = 2;       // 机构ID
    optional int32 changeType = 3;          // HoldingChangeType, 按变动类型筛选(不传=全部)
    optional int32 sortField = 4;           // SortField
    optional int32 sortDir = 5;             // SortDir
    optional int32 count = 6;               // 条数 [1,200], 默认20
    optional string page = 7;               // 翻页游标, 首次不传
    optional string keyword = 8;            // 搜索关键词(股票名/代码)
}

// 持股列表数据项
message HoldingListItem {
    required Qot_Common.Security security = 1;  // 股票
    optional string name = 2;                    // 名称
    optional string industryName = 3;            // 所属行业
    optional double holdingValue = 4;            // 持股市值
    optional double holdingPct = 5;              // 持股比例-占股票总市值(%)
    optional double lastHoldingPct = 6;          // 上期持股比例(%)
    optional int64 changeShares = 7;             // 变动股数
    optional double portfolioPct = 8;            // 占机构总仓位比例(%)
    optional double changePct = 9;               // 变动比例(%)
    optional string holdingDate = 10;            // 持仓时间(yyyy-MM-dd)
    optional string source = 11;                 // 披露来源
}

message S2C {
    repeated HoldingListItem dataList = 1;      // 数据列表
    optional int32 allCount = 2;                // 总数
    optional string nextPage = 3;               // 下一页游标, 空=无更多
    optional string currency = 4;               // 币种
}

message Request {
    required C2S c2s = 1;
}

message Response {
    required int32 retType = 1 [default = -400]; // RetType, 返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3422


* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetInstitutionHoldingList(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11111, false, "xxxxxx"];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: { market: 11, institutionId: 403413, count: 3 },
            };
            websocket.GetInstitutionHoldingList(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetInstitutionHoldingList: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetInstitutionHoldingList()
```

* **Output**

``` JavaScript
GetInstitutionHoldingList: errCode 0, retMsg , retType 0
{
  "allCount": 4431,
  "currency": "USD",
  "dataList": [
    { "security": { "market": 11, "code": "NVDA" }, "name": "英伟达", "holdingValue": 404647000000.0, "holdingPct": 7.9295 },
    { "security": { "market": 11, "code": "AAPL" }, "name": "苹果", "holdingValue": 339306000000.0, "holdingPct": 7.7520 },
    { "security": { "market": 11, "code": "GOOGL" }, "name": "谷歌-A", "holdingValue": 298400000000.0, "holdingPct": 6.6443 }
  ]
}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取ARK基金持仓

`getArkFundHolding(qotGetArkFundHolding)`


* **介绍**

    协议请求与返回定义

* **参数**

```protobuf
// ARK持仓类型
enum ArkHoldingType {
    ArkHoldingType_Position = 0;        // 持仓
    ArkHoldingType_Increase = 1;        // 增持
    ArkHoldingType_Decrease = 2;        // 减持
    ArkHoldingType_New = 3;             // 建仓
    ArkHoldingType_SoldOut = 4;         // 清仓
}

// 周期类型
enum CycleType {
    CycleType_1Day = 0;                 // 近1天
    CycleType_5Day = 1;                 // 近5天
    CycleType_10Day = 2;                // 近10天
    CycleType_30Day = 3;                // 近30天
    CycleType_60Day = 4;                // 近60天
}

// 排序字段
enum SortField {
    SortField_Shares = 0;               // 持仓数量(默认)
    SortField_WeightChange = 1;         // 占比变动
    SortField_SharesChange = 2;         // 持仓变动
    SortField_MarketValue = 3;          // 市值
    SortField_Weight = 4;               // ETF占比
}

// 排序方向
enum SortDir {
    SortDir_Descending = 0;     // 降序(默认)
    SortDir_Ascending = 1;      // 升序
}

message C2S {
    optional int32 holdingType = 1;         // ArkHoldingType, 默认持仓
    optional int32 cycleType = 2;           // CycleType, 默认近1天(holdingType=持仓时忽略)
    optional int32 sortField = 3;           // SortField, 默认按持仓数量降序
    optional int32 sortDir = 4;             // SortDir
    optional int32 count = 5;               // 条数 [1,200], 默认20
    optional string page = 6;               // 翻页游标, 首次不传
}

// ARK基金持仓数据项
message ArkFundHoldingItem {
    optional Qot_Common.Security security = 1;  // 股票(stock_id有效时)
    optional string name = 2;                    // 名称
    optional int64 shares = 3;                   // 持仓数量
    optional int64 sharesChange = 4;             // 持仓数量变动
    optional double marketValue = 5;             // 持仓市值(美元)
    optional double weight = 6;                  // 持仓占比(%)
    optional double weightChange = 7;            // 持仓占比变动(%)
}

message S2C {
    repeated ArkFundHoldingItem dataList = 1;   // 数据列表
    optional int32 allCount = 2;                // 总数
    optional string nextPage = 3;               // 下一页游标, 空=无更多
}

message Request {
    required C2S c2s = 1;
}

message Response {
    required int32 retType = 1 [default = -400]; // RetType, 返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3423


* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetArkFundHolding(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11111, false, "xxxxxx"];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: { count: 3 },
            };
            websocket.GetArkFundHolding(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetArkFundHolding: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetArkFundHolding()
```

* **Output**

``` JavaScript
GetArkFundHolding: errCode 0, retMsg , retType 0
{
  "allCount": 20,
  "dataList": [
    { "security": { "market": 11, "code": "RXRX" }, "name": "Recursion Pharmaceuticals", "shares": 31742578, "marketValue": 102528500.0, "weight": 0.72 },
    { "security": { "market": 11, "code": "ACHR" }, "name": "Archer Aviation", "shares": 29701570, "marketValue": 165437700.0, "weight": 1.17 }
  ]
}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取ARK个股交易动态

`getArkStockDynamic(qotGetArkStockDynamic)`


* **介绍**

    获取 ARK 个股交易动态，返回指定股票在 ARK 基金中的最新交易动态信息（连续同向交易、近期交易、最近一笔等）。

* **参数**

```protobuf
// 交易动态类型
enum DynamicType {
    DynamicType_Unknown = 0;
    DynamicType_ConsecutiveSameDirection = 1;    // 连续同向交易
    DynamicType_RecentTransaction = 2;           // 近期交易
    DynamicType_LastTransaction = 3;             // 最近一笔
    DynamicType_NoDynamic = 4;                   // 无动态
}

message C2S {
    required Qot_Common.Security security = 1;   // 股票
}

message S2C {
    optional int32 dynamicType = 1;              // DynamicType
    optional int32 transactionCount = 2;         // 交易次数
    optional int64 netShares = 3;                // 净交易股数
    optional string lastTransactionTime = 4;     // 最近交易时间(yyyy-MM-dd)
}

message Request {
    required C2S c2s = 1;
}

message Response {
    required int32 retType = 1 [default = -400]; // RetType, 返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3424


* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetArkStockDynamic(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11111, false, "xxxxxx"];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: { security: { market: Qot_Common.QotMarket.QotMarket_US_Security, code: "TSLA" } },
            };
            websocket.GetArkStockDynamic(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetArkStockDynamic: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetArkStockDynamic()
```

* **Output**

``` JavaScript
GetArkStockDynamic: errCode 0, retMsg , retType 0
{
  "dynamicType": 1,
  "transactionCount": 3,
  "netShares": -29523,
  "lastTransactionTime": "2026-06-17"
}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取ARK主动交易聚合

`getArkActiveTransaction(qotGetArkActiveTransaction)`


* **介绍**

    协议请求与返回定义

* **参数**

```protobuf
// 持仓变动类型
enum HoldingType {
    HoldingType_Increase = 0;           // 增持(默认)
    HoldingType_Decrease = 1;           // 减持
    HoldingType_New = 2;                // 建仓
    HoldingType_SoldOut = 3;            // 清仓
}

// 周期类型
enum CycleType {
    CycleType_1Day = 0;                 // 近1天
    CycleType_5Day = 1;                 // 近5天
    CycleType_10Day = 2;                // 近10天
    CycleType_30Day = 3;                // 近30天
    CycleType_60Day = 4;                // 近60天
}

// 排序字段
enum SortField {
    SortField_Unknown = 0;              // 默认(变动金额)
    SortField_ChangeAmount = 1;         // 变动金额
    SortField_ChangeShares = 2;         // 变动股数
}

// 排序方向
enum SortDir {
    SortDir_Descending = 0;             // 降序(默认,净买入在前)
    SortDir_Ascending = 1;              // 升序(净卖出在前)
}

message C2S {
    optional int32 holdingType = 1;         // HoldingType, 默认增持
    optional int32 cycleType = 2;           // CycleType, 默认近1天
    optional int32 sortField = 3;           // SortField
    optional int32 sortDir = 4;             // SortDir
    optional int32 count = 5;              // 条数 [1,200], 默认50
    optional string page = 6;              // 翻页游标, 首次不传
}

// ARK主动交易数据项
message ArkActiveTransactionItem {
    optional Qot_Common.Security security = 1;  // 股票
    optional string name = 2;                    // 名称
    optional double changeAmount = 3;            // 变动金额(美元)
    optional int64 changeShares = 4;             // 变动数量(股)
}

message S2C {
    repeated ArkActiveTransactionItem dataList = 1; // 数据列表
    optional int32 allCount = 2;                    // 总数
    optional string nextPage = 3;                   // 下一页游标, 空=无更多
}

message Request {
    required C2S c2s = 1;
}

message Response {
    required int32 retType = 1 [default = -400]; // RetType, 返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3425


* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetArkActiveTransaction(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11111, false, "xxxxxx"];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: { count: 3 },
            };
            websocket.GetArkActiveTransaction(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetArkActiveTransaction: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetArkActiveTransaction()
```

* **Output**

``` JavaScript
GetArkActiveTransaction: errCode 0, retMsg , retType 0
{
  "allCount": 5,
  "dataList": [
    { "security": { "market": 11, "code": "SNOW" }, "name": "Snowflake", "changeAmount": 51960949.0, "changeShares": 223690 },
    { "security": { "market": 11, "code": "TSLA" }, "name": "特斯拉", "changeAmount": 21952859.0, "changeShares": 54815 },
    { "security": { "market": 11, "code": "LLY" }, "name": "礼来", "changeAmount": 9323563.0, "changeShares": 8487 }
  ]
}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取评级变动

`getRatingChange(qotGetRatingChange)`


* **介绍**

    协议请求与返回定义

* **参数**

```protobuf
// 评级变动类型
enum RatingChangeType {
    RatingChangeType_Upgrade = 1;       // 评级上调
    RatingChangeType_Downgrade = 2;     // 评级下调
    RatingChangeType_NewRating = 3;     // 首次评级
}

// 评级等级
enum RatingLevel {
    RatingLevel_Unknown = 0;
    RatingLevel_Sell = 1;               // 卖出
    RatingLevel_Hold = 2;               // 持有
    RatingLevel_Buy = 3;                // 买入
}

message C2S {
    required int32 market = 1;              // Qot_Common.QotMarket (仅US/CA)
    optional int32 changeType = 2;          // RatingChangeType, 默认上调
    optional int32 count = 3;               // 条数 [1,20], 默认10
    optional string page = 4;               // 翻页游标, 首次不传
}

message RatingChangeItem {
    optional Qot_Common.Security security = 1;  // 股票
    optional string name = 2;                    // 名称
    optional int32 rating = 3;                   // 当前评级 RatingLevel
    optional int32 lastRating = 4;               // 上次评级 RatingLevel
    optional double targetPrice = 5;             // 当前目标价
    optional double lastTargetPrice = 6;         // 上次目标价
    optional int32 changeType = 7;               // RatingChangeType
    optional string institutionName = 8;         // 机构名称
    optional string recommendationDate = 9;       // 推荐日期(字符串,如"2025-06-15")
    optional string lastRecommendationDate = 10;  // 上次推荐日期(字符串,如"2025-06-15")
}

message S2C {
    repeated RatingChangeItem dataList = 1;
    optional int32 allCount = 2;            // 总数
    optional string nextPage = 3;           // 下一页游标, 空=无更多
}

message Request {
    required C2S c2s = 1;
}

message Response {
    required int32 retType = 1 [default = -400]; // RetType, 返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3426


* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetRatingChange(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11111, false, "xxxxxx"];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: { market: 11, count: 3 },
            };
            websocket.GetRatingChange(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetRatingChange: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetRatingChange()
```

* **Output**

``` JavaScript
GetRatingChange: errCode 0, retMsg , retType 0
{
  "allCount": 5907,
  "dataList": [
    { "security": { "market": 11, "code": "MU" }, "name": "美光科技", "changeType": 1, "institutionName": "Needham", "targetPrice": 1550.0 },
    { "security": { "market": 11, "code": "MU" }, "name": "美光科技", "changeType": 1, "institutionName": "联博集团", "targetPrice": 1300.0 },
    { "security": { "market": 11, "code": "NUE" }, "name": "纽柯钢铁", "changeType": 1, "institutionName": "摩根士丹利", "targetPrice": 258.0 }
  ]
}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取产业链列表

`getIndustrialChainList(qotGetIndustrialChainList)`


* **介绍**

    获取产业链列表，返回指定市场的产业链信息（含产业链类型、市值、成分股数量等），支持关键字搜索和游标翻页。

* **参数**

```protobuf
// 产业链类型
enum IndustrialChainType {
    IndustrialChainType_Chain = 1;      // 串联型
    IndustrialChainType_Parallel = 2;   // 并列型
    IndustrialChainType_UpMidDown = 3;  // 上中下游型
}

message C2S {
    required int32 market = 1;          // Qot_Common.QotMarket
    optional string keyword = 2;        // 搜索关键字(可选)
    optional int32 count = 3;           // 条数 [1,50], 默认20
    optional string page = 4;           // 翻页游标, 首次不传
}

message IndustrialChainInfo {
    optional int64 chainId = 1;                             // 产业链ID
    optional int32 chainType = 2;                           // IndustrialChainType
    optional string name = 3;                               // 名称
    optional string detail = 4;                             // 详情描述
    optional double marketCap = 5;                          // 市值
    optional int64 stocksNum = 6;                           // 成分股数量
    repeated Qot_Common.Security relationSecurityList = 7;  // 相关股票
}

message S2C {
    repeated IndustrialChainInfo dataList = 1;
    optional int32 allCount = 2;
    optional string nextPage = 3;
}

message Request {
    required C2S c2s = 1;
}

message Response {
    required int32 retType = 1 [default = -400];
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3427


* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetIndustrialChainList(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11111, false, "xxxxxx"];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: { market: 11, count: 3 },
            };
            websocket.GetIndustrialChainList(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetIndustrialChainList: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetIndustrialChainList()
```

* **Output**

``` JavaScript
GetIndustrialChainList: errCode 0, retMsg , retType 0
{
  "allCount": 70,
  "dataList": [
    { "chainId": "9610020", "name": "AI", "chainType": 1, "stocksNum": 329 },
    { "chainId": "9610085", "name": "商业航天", "chainType": 1, "stocksNum": 155 },
    { "chainId": "9610033", "name": "半导体", "chainType": 1, "stocksNum": 256 }
  ]
}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取产业链详情

`getIndustrialChainDetail(qotGetIndustrialChainDetail)`


* **介绍**

    获取产业链详情，返回指定产业链的完整结构信息，包含层级节点列表和相关资讯链接。

* **参数**

```protobuf
message C2S {
    required int64 chainId = 1;         // 产业链ID
}

message IndustrialChainNode {
    optional int64 nodeId = 1;              // 节点ID
    optional int64 parentNodeId = 2;        // 父节点ID (根节点为0)
    optional int64 layerSth = 3;            // 节点层级(从1开始)
    optional string name = 4;               // 节点名称
    optional int64 plateId = 5;             // 关联板块ID(可选)
}

message InformationLink {
    optional string title = 1;          // 资讯标题
    optional string url = 2;            // 资讯链接
}

message S2C {
    optional int64 chainId = 1;                         // 产业链ID
    optional int32 chainType = 2;                       // 类型
    optional string name = 3;                           // 名称
    repeated IndustrialChainNode nodeList = 4;          // 节点列表(按层级分组)
    repeated InformationLink informationList = 5;       // 资讯链接
}

message Request {
    required C2S c2s = 1;
}

message Response {
    required int32 retType = 1 [default = -400];
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3428


* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetIndustrialChainDetail(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11111, false, "xxxxxx"];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: { chainId: 9610020 },
            };
            websocket.GetIndustrialChainDetail(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetIndustrialChainDetail: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetIndustrialChainDetail()
```

* **Output**

``` JavaScript
GetIndustrialChainDetail: errCode 0, retMsg , retType 0
{
  "chainId": "9610020",
  "name": "AI",
  "chainType": 1,
  "nodeList": [
    { "plateName": "基础建设层", "level": 1 },
    { "plateName": "算法层", "level": 1 },
    { "plateName": "应用层", "level": 1, "plateId": "10010508" }
  ]
}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取板块关联产业链

`getIndustrialChainByPlate(qotGetIndustrialChainByPlate)`


* **介绍**

    获取板块关联产业链，返回指定产业板块所关联的产业链列表信息（含类型、市值、成分股数量）。

* **参数**

```protobuf
message C2S {
    required int64 plateId = 1;             // 产业板块ID
}

message RelatedChainInfo {
    optional int64 chainId = 1;             // 产业链ID
    optional int32 chainType = 2;           // 类型
    optional string name = 3;               // 名称
    optional double marketCap = 4;          // 市值
    optional int64 stocksNum = 5;           // 成分股数量
}

message S2C {
    repeated RelatedChainInfo relatedChainList = 1;    // 关联的产业链
}

message Request {
    required C2S c2s = 1;
}

message Response {
    required int32 retType = 1 [default = -400];
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3429


* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetIndustrialChainByPlate(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11111, false, "xxxxxx"];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: { plateId: 10010508 },
            };
            websocket.GetIndustrialChainByPlate(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetIndustrialChainByPlate: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetIndustrialChainByPlate()
```

* **Output**

``` JavaScript
GetIndustrialChainByPlate: errCode 0, retMsg , retType 0
{
  "relatedChainList": [
    { "chainId": "9610020", "name": "AI", "chainType": 1, "stocksNum": 329 }
  ]
}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取产业板块信息

`getIndustrialPlateInfo(qotGetIndustrialPlateInfo)`


* **介绍**

    获取产业板块信息，返回指定产业板块的简介信息。

* **参数**

```protobuf
message C2S {
    required int64 plateId = 1;             // 产业板块ID
}

message S2C {
    optional int64 plateId = 1;             // 板块ID
    optional string summary = 2;            // 板块简介
}

message Request {
    required C2S c2s = 1;
}

message Response {
    required int32 retType = 1 [default = -400];
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3430


* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetIndustrialPlateInfo(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11111, false, "xxxxxx"];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: { plateId: 10010508 },
            };
            websocket.GetIndustrialPlateInfo(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetIndustrialPlateInfo: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetIndustrialPlateInfo()
```

* **Output**

``` JavaScript
GetIndustrialPlateInfo: errCode 0, retMsg , retType 0
{
  "plateId": "10010508",
  "summary": ""
}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取产业板块成分股

`getIndustrialPlateStock(qotGetIndustrialPlateStock)`


* **介绍**

    协议请求与返回定义

* **参数**

```protobuf
// 排序字段
enum SortField {
    SortField_Code = 0;           //代码(默认)
    SortField_ChangeRate = 1;     //涨跌幅
    SortField_Turnover = 2;       //成交额
    SortField_Volume = 3;         //成交量
    SortField_MarketVal = 4;      //市值
}

message StockInfo
{
    optional Qot_Common.Security security = 1; //股票
    optional string name = 2; //股票名称
}

message C2S
{
    optional int64 chainId = 1;        //产业链ID (与plateId二选一，plateId优先)
    optional int64 plateId = 2;        //产业板块ID (优先使用)
    repeated int32 marketList = 3;     //Qot_Common.QotMarket 市场筛选(支持HK/US/CN/JP/SG/MY，不传默认全部)
    optional int32 sortField = 4;      //SortField，排序字段，默认MarketVal(市值)
    optional bool ascend = 5;          //升序true/降序false，默认false(降序)
    optional int32 count = 6;          //每页数量 [1,200], 默认50
    optional string page = 7;          //翻页标记，首次不传，后续带上S2C返回的page
}

message S2C
{
    repeated StockInfo stockList = 1;  //成分股列表
    optional string page = 2;          //翻页标记，有更多数据时返回
    optional int32 allCount = 3;       //总数量
}

message Request
{
    required C2S c2s = 1;
}

message Response
{
    required int32 retType = 1 [default = -400]; //RetType,返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3431


* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetIndustrialPlateStock(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11111, false, "xxxxxx"];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: { plateId: 10010508, count: 5 },
            };
            websocket.GetIndustrialPlateStock(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetIndustrialPlateStock: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetIndustrialPlateStock()
```

* **Output**

``` JavaScript
GetIndustrialPlateStock: errCode 0, retMsg , retType 0
{
  "allCount": 111,
  "stockList": [
    { "security": { "market": 11, "code": "NVDA" }, "name": "英伟达" },
    { "security": { "market": 11, "code": "GOOGL" }, "name": "谷歌-A" },
    { "security": { "market": 11, "code": "GOOG" }, "name": "谷歌-C" },
    { "security": { "market": 11, "code": "AAPL" }, "name": "苹果" },
    { "security": { "market": 11, "code": "MSFT" }, "name": "微软" }
  ]
}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取热力图数据

`getHeatMapData(qotGetHeatMapData)`


* **介绍**

    协议请求与返回定义

* **参数**

```protobuf
//热力图板块类型
enum HeatMapPlateType
{
	HeatMapPlateType_Industry = 0; //行业板块(默认)
	HeatMapPlateType_Concept = 1;  //概念板块
	HeatMapPlateType_Theme = 2;    //主题板块
}

//排序字段
enum SortField
{
	SortField_Unknow = 0;
	SortField_ChangeRate = 1; //涨跌幅
	SortField_MarketVal = 2; //市值
	SortField_Turnover = 3; //成交额
	SortField_Hot = 4; //热度
}

message C2S
{
	required int32 market = 1; //Qot_Common.QotMarket,股票市场
	optional int32 sortField = 2; //SortField,排序字段,不填默认涨跌幅
	optional bool ascend = 3; //升序true,降序false,不填默认降序
	optional int32 count = 4; //返回条数[1,200],不填默认30
	optional string page = 5; //翻页游标,首次不传,后续传上次返回的nextPage
	optional int32 plateType = 6; //HeatMapPlateType,板块类型,不填默认行业板块
}

message HeatMapPlateData
{
	optional Qot_Common.Security plate = 1; //板块
	optional string plateName = 2; //板块名称
	optional double curPrice = 3; //最新价
	optional double changeRate = 4; //涨跌幅(%)
	optional double turnover = 5; //成交额
	optional int64 volume = 6; //成交量
	optional double marketVal = 7; //市值
	optional double peAvg = 8; //平均市盈率
	optional int32 riseCount = 9; //涨家数
	optional int32 fallCount = 10; //跌家数
	optional int32 equalCount = 11; //持平数
	optional Qot_Common.Security leaderStock = 12; //领涨股
	optional string description = 13; //板块描述
}

message S2C
{
	repeated HeatMapPlateData plateDataList = 1; //板块数据列表
	optional int32 allCount = 2; //板块总数
	optional string nextPage = 3; //下一页游标,空表示最后一页
}

message Request
{
	required C2S c2s = 1;
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType,返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;

	optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3432


* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetHeatMapData(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11111, false, "xxxxxx"];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: { market: 11, count: 3 },
            };
            websocket.GetHeatMapData(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetHeatMapData: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetHeatMapData()
```

* **Output**

``` JavaScript
GetHeatMapData: errCode 0, retMsg , retType 0
{
  "allCount": 145,
  "plateDataList": [
    { "plate": { "market": 11, "code": "LIST2479" }, "plateName": "抵押贷款金融", "changeRate": 7.543126 },
    { "plate": { "market": 11, "code": "LIST2493" }, "plateName": "电气设备及零件", "changeRate": 6.800033 },
    { "plate": { "market": 11, "code": "LIST2015" }, "plateName": "半导体", "changeRate": 5.358499 }
  ]
}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 获取涨跌分布

`getRiseFallDistribution(qotGetRiseFallDistribution)`


* **介绍**

    协议请求与返回定义

* **参数**

```protobuf
//涨跌分布类型
enum DistributionType
{
	DistributionType_Unknown = 0; //未知
	DistributionType_RiseLimit = 1; //涨停(A股)
	DistributionType_PositiveInfinity = 2; //(7%, +∞)
	DistributionType_NormalRange = 3; //正常区间
	DistributionType_NegativeInfinity = 4; //(-∞, -7%)
	DistributionType_FallLimit = 5; //跌停(A股)
}

message C2S
{
	optional Qot_Common.Security security = 1; //板块(优先使用)
	optional int32 market = 2; //Qot_Common.QotMarket,市场(security未传时使用)
}

message RiseFallRange
{
	optional int32 type = 1; //DistributionType,分布类型
	optional int32 leftBorder = 2; //左边界值
	optional int32 rightBorder = 3; //右边界值
	optional int32 stockCount = 4; //区间股票数
}

message S2C
{
	optional Qot_Common.Security plate = 1; //板块
	repeated RiseFallRange rangeList = 2; //涨跌分布区间列表
}

message Request
{
	required C2S c2s = 1;
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType,返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;

	optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3433


* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetRiseFallDistribution(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 11111, false, "xxxxxx"];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: { market: 11 },
            };
            websocket.GetRiseFallDistribution(req)
            .then((res)=>{
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetRiseFallDistribution: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
                    console.log(data);
                }
            })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetRiseFallDistribution()
```

* **Output**

``` JavaScript
GetRiseFallDistribution: errCode 0, retMsg , retType 0
{
  "plate": { "market": 11, "code": "USAALL" },
  "rangeList": [
    { "rangeType": 3, "rangeMin": 7.0, "count": 712 },
    { "rangeType": 1, "rangeMin": -5.0, "rangeMax": -3.0, "count": 546 },
    { "rangeType": 1, "rangeMin": -3.0, "rangeMax": 0.0, "count": 3132 },
    { "rangeType": 1, "rangeMin": 0.0, "rangeMax": 0.0, "count": 4294 },
    { "rangeType": 1, "rangeMin": 5.0, "rangeMax": 7.0, "count": 436 }
  ]
}
```

:::tip 接口限制
- 30 秒内最多 60 次请求
- 分页请求仅首页计入限频统计
:::

---

# 市场定义

## ARK主动交易持仓变动类型


## ARK主动交易排序字段


## ARK周期类型


## ARK基金持仓排序字段


## ARK持仓类型


## 财报超预期时间范围


## 财报超预期类型


## 派息频率类型


## 股息排行排序字段


## 股息排行类型


## 财报超预期排序字段


## 财报指标类型


## 财报发布时段类型


## 财报日历排序类型


## 财报日历股票列表类型


## 经济数据重要性


## 热力图板块类型


## 热力图排序字段


## 高息国企排序字段


## 热门排行排序字段


## 机构持仓变动排序字段


## 机构持仓变动类型


## 机构持仓列表排序字段


## 机构列表排序字段


## 宏观数据单位类型


## 宏观经济地区


## 产业链板块股票排序字段


## 价格筛选类型


## 排行榜周期类型


## 排行榜排序方向


## 评级变动类型


## 做空排行排序字段

---

# 获取指标列表

`GetIndicatorList(req);`

* **介绍**

    获取指标列表（可按关键词、语言类型、匹配方式过滤）。

* **参数**

```protobuf
message C2S
{
    optional string searchKey = 1;
    optional int32 langType = 2;
    optional int32 searchMode = 3;
}

message Request
{
    required C2S c2s = 1;
}
```

* **返回**

```protobuf
message IndicatorInfo
{
    optional string shortName = 1;
    optional string fullName = 2;
    repeated Qot_Common.IndicatorInputParam inputs = 3;
    repeated Qot_Common.IndicatorOutputParam outputs = 4;
    optional string script = 5;
}

message IndicatorEntry
{
    optional IndicatorInfo myLang = 1;
    optional IndicatorInfo python = 2;
}

message S2C
{
    repeated IndicatorEntry indicatorList = 1;
}

message Response
{
    required int32 retType = 1 [default = -400];
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetIndicatorList(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: {
                    searchKey: "MA",
                    langType: 1,
                    searchMode: 0,
                },
            };

            websocket.GetIndicatorList(req)
            .then((res) => {
                let { errCode, retMsg, retType, s2c } = res
                console.log("GetIndicatorList: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotGetIndicatorList()
```

* **Output**

``` JavaScript
GetIndicatorList: errCode 0, retMsg , retType 0
{
  "indicatorList": [
    {
      "myLang": {
        "shortName": "MA",
        "fullName": "简单移动平均线",
        "inputs": [
          { "index": 0, "name": "price", "type": 1 },
          { "index": 1, "name": "period", "type": 0 }
        ],
        "outputs": [
          { "index": 0, "name": "MA", "type": 1 }
        ]
      },
      "python": {
        "shortName": "MA",
        "fullName": "简单移动平均线",
        "inputs": [
          { "index": 0, "name": "close", "type": 1 },
          { "index": 1, "name": "period", "type": 0 }
        ],
        "outputs": [
          { "index": 0, "name": "MA", "type": 1 }
        ]
      }
    },
    {
      "myLang": {
        "shortName": "MACD",
        "fullName": "指数平滑移动平均线",
        "inputs": [
          { "index": 0, "name": "price", "type": 1 },
          { "index": 1, "name": "SHORT", "type": 0 },
          { "index": 2, "name": "LONG", "type": 0 },
          { "index": 3, "name": "MID", "type": 0 }
        ],
        "outputs": [
          { "index": 0, "name": "DIF", "type": 1 },
          { "index": 1, "name": "DEA", "type": 1 },
          { "index": 2, "name": "MACD", "type": 1 }
        ]
      }
    }
  ]
}
```

:::tip 接口限制
* 每 30 秒内最多请求 10 次获取指标列表接口。
:::
</content>
</invoke>

---

# 异步发起指标计算

`RequestIndicatorCalc(req);`

* **介绍**

    异步发起指标计算。接口立即返回 calcId，实际结果由 PushIndicatorCalc(3261) 推送。

* **参数**

```protobuf
message IndicatorInputItem
{
    required int32 index = 1;
    optional string value = 2;
}

message IndicatorCalcData
{
    required Qot_Common.Security security = 1;
    required Qot_Common.KLType klType = 2;
    repeated Qot_Common.KLine kLine = 3;
}

message C2S
{
    required string shortName = 1;
    required Qot_Common.IndicatorLangType langType = 2;
    required IndicatorCalcData data = 3;
    optional int32 num = 4;
    repeated IndicatorInputItem inputs = 5;
}

message Request
{
    required C2S c2s = 1;
}
```

* **返回**

```protobuf
message S2C
{
    required string calcId = 1;
}

message Response
{
    required int32 retType = 1 [default = -400];
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotRequestIndicatorCalc(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            const req = {
                c2s: {
                    shortName: "MA",
                    langType: 1,
                    data: {
                        security: { market: 1, code: "00700" },
                        klType: 2,
                        kLine: [],
                    },
                    num: 60,
                    inputs: [{ index: 0, value: "20" }],
                },
            };

            websocket.RequestIndicatorCalc(req)
            .then((res) => {
                let { errCode, retMsg, retType, s2c } = res
                console.log("RequestIndicatorCalc: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotRequestIndicatorCalc()
```

* **Output**

``` JavaScript
RequestIndicatorCalc: errCode 0, retMsg , retType 0
{
  "calcId": "1700000000000-0"
}
```

:::tip 接口限制
* 每 30 秒内最多发起 10 次指标计算请求。
* 实际计算结果通过 [Qot_PushIndicatorCalc](./push-indicator-calc.md)(3261) 异步推送，需提前注册推送回调。
:::
</content>
</invoke>

---

# 指标异步计算结果推送

`onPush_PushIndicatorCalc(qotPushIndicatorCalc)`

* **介绍**

    指标异步计算结果推送回调。需通过 [`RequestIndicatorCalc`](./request-indicator-calc.md) 发起计算后被动接收，使用 calcId 与请求配对。

* **参数**

```protobuf
//一行计算结果，对应一个 K 线时刻；values 顺序与 outputs 一一对应
message IndicatorOutputRow
{
    optional string time = 1;    //K 线时间（与请求中的 KLine.time 一致）
    repeated double values = 2;  //各输出线在该时刻的值
}

message S2C
{
    required string calcId = 1;                            //与发起请求时返回的 calcId 对应
    repeated Qot_Common.IndicatorOutputParam outputs = 2;  //输出线元数据
    repeated IndicatorOutputRow outputRows = 3;            //计算结果，按时间顺序
}

message Response
{
    required int32 retType = 1 [default = -400]; //RetType，返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```
>    - 指标输出参数结构参见 [IndicatorOutputParam](./quote.md#916)
>    - 发起指标计算参见 [Qot_RequestIndicatorCalc](./request-indicator-calc.md)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **协议 ID**

    3261

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotPushIndicatorCalc(){
    const { RetType } = Common
    const { KLType, IndicatorLangType, QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    // 注册指标异步计算结果推送回调，与 RequestIndicatorCalc 返回的 calcId 配对
    websocket.onPush_PushIndicatorCalc = (qotPushIndicatorCalc)=>{
        let { errCode, retMsg, retType, s2c } = qotPushIndicatorCalc
        console.log("PushIndicatorCalc: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType);
        if(retType == RetType.RetType_Succeed){
            let data = beautify(JSON.stringify(s2c), { indent_size: 2, space_in_empty_paren: true });
            console.log(data);
        }
    };

    websocket.onlogin = (ret, msg)=>{
        if (ret) {
            // 发起一次 MACD 指标计算，结果由上面的回调推送回来
            const req = {
                c2s: {
                    shortName: "MACD",
                    langType: IndicatorLangType.IndicatorLangType_MyLang,
                    data: {
                        security: { market: QotMarket.QotMarket_HK_Security, code: "00700" },
                        klType: KLType.KLType_Day,
                        kLine: [
                            { time: 1700000000, open: 310.0, close: 315.0, high: 318.0, low: 308.0, volume: 10000000, turnover: 3150000000 }
                        ]
                    },
                },
            };
            websocket.RequestIndicatorCalc(req)
            .then((res)=>{ console.log("RequestIndicatorCalc calcId:", res.s2c && res.s2c.calcId); })
            .catch((error)=>{ console.log("error:", error); });
        } else {
            console.log("start error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    setTimeout(()=>{ websocket.stop(); process.exit(); }, 5000);
}

QotPushIndicatorCalc()
```

* **Output**

``` JavaScript
RequestIndicatorCalc calcId: 1700000000000-0
PushIndicatorCalc: errCode 0, retMsg , retType 0
{
  "calcId": "1700000000000-0",
  "outputs": [
    { "index": 0, "name": "DIF", "type": 1 },
    { "index": 1, "name": "DEA", "type": 1 },
    { "index": 2, "name": "MACD", "type": 1 }
  ],
  "outputRows": [
    { "time": "1700000000", "values": [0.5234, 0.4123, 0.2222] }
  ]
}
```

:::tip 说明
* 本接口仅作为推送通道，无对应的主动请求，结果由 [Qot_RequestIndicatorCalc](./request-indicator-calc.md)(3260) 触发。
:::
</content>
</invoke>

---

# 获取历史 K 线额度使用明细

`RequestHistoryKLQuota(req);`

* **介绍**

    获取历史 K 线额度使用明细

* **参数**

```protobuf
message C2S
{
	optional bool bGetDetail = 2;	//是否返回详细拉取过的历史纪录
}

message Request
{
	required C2S c2s = 1;
}
```

* **返回**

```protobuf
message DetailItem
{
	required Qot_Common.Security security = 1;	//拉取的股票
    optional string name = 4; //股票名称
	required string requestTime = 2;    	//拉取的时间字符串（格式：yyyy-MM-dd HH:mm:ss）
	optional int64 requestTimeStamp = 3;        //拉取的时间戳
}

message S2C
{
	required int32 usedQuota = 1;	      //已使用过的额度，即当前周期内已经下载过多少只股票。
	required int32 remainQuota = 2;       //剩余额度
	repeated DetailItem detailList = 3;	  //每只拉取过的股票的下载时间
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType，返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotRequestHistoryKLQuota(){
    const { RetType } = Common
    const {  } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功

            const req = {
                c2s: {
                    bGetDetail: true,
                },
            };

            websocket.RequestHistoryKLQuota(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("HistoryKLQuota: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
HistoryKLQuota: errCode 0, retMsg , retType 0
{
  "usedQuota": 1,
  "remainQuota": 99,
  "detailList": [{
    "security": {
      "market": 1,
      "code": "00700"
    },
    "requestTime": "2021-09-10 14:17:17",
    "requestTimeStamp": "1631254637"
  }]
}
stop
```


:::tip 接口限制
* 我们会根据您账户的资产和交易的情况，下发历史 K 线额度。因此，7 天内您只能获取有限只股票的历史 K 线数据。具体规则参见 [订阅额度 & 历史 K 线额度](../intro/authority.md#1314)。
* 您当日消耗的历史 K 线额度，会在 7 天后自动释放。
:::

---

# 设置到价提醒

`SetPriceReminder(req);`

* **介绍**

    新增、删除、修改、启用、禁用指定股票的到价提醒

* **参数**

```protobuf
enum SetPriceReminderOp
{
	SetPriceReminderOp_Unknown = 0;
	SetPriceReminderOp_Add = 1; //新增
	SetPriceReminderOp_Del = 2; //删除
	SetPriceReminderOp_Enable = 3; //启用
	SetPriceReminderOp_Disable = 4; //禁用
	SetPriceReminderOp_Modify = 5; //修改
	SetPriceReminderOp_DelAll = 6; //删除该支股票下所有到价提醒
}

message C2S
{
	required Qot_Common.Security security = 1; // 股票
	required int32 op = 2; // SetPriceReminderOp，操作类型
	optional int64 key = 3; // 到价提醒的标识，GetPriceReminder 协议可获得，用于指定要操作的到价提醒项，对于新增的情况不需要填
	optional int32 type = 4; // Qot_Common::PriceReminderType，提醒类型，删除、启用、禁用的情况下会忽略该字段
	optional int32 freq = 7; // Qot_Common::PriceReminderFreq，提醒频率类型，删除、启用、禁用的情况下会忽略该字段
	optional double value = 5; // 提醒值，删除、启用、禁用的情况下会忽略该字段（精确到小数点后 3 位，超出部分会被舍弃）
	optional string note = 6; // 用户设置到价提醒时的标注，仅支持 20 个以内的中文字符，删除、启用、禁用的情况下会忽略该字段
    repeated int32 reminderSessionList = 8; // 到价提醒的时段列表，删除、启用、禁用的情况下会忽略该入参,枚举参考Qot_Common::PriceReminderMarketStatus
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 提醒类型枚举参见 [PriceReminderType](./quote.md#5160)
>    - 提醒频率枚举参见 [PriceReminderFreq](./quote.md#1059)

* **返回**

```protobuf
message S2C
{
	required int64 key = 1; //设置成功的情况下返回对应的 key，不成功返回0
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType，返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common, Qot_SetPriceReminder } from "futu-api/proto";
import beautify from "js-beautify";

function QotSetPriceReminder(){
    const { RetType } = Common
    const { PriceReminderType, PriceReminderFreq, QotMarket } = Qot_Common
    const { SetPriceReminderOp } = Qot_SetPriceReminder
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功

            const req = {
                c2s: {
                    security: {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                    op: SetPriceReminderOp.SetPriceReminderOp_Add,
                    type: PriceReminderType.PriceReminderType_PriceUp,
                    freq: PriceReminderFreq.PriceReminderFreq_Always,
                    value: 600,
                },
            };
            websocket.SetPriceReminder(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("PriceReminder: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
PriceReminder: errCode 0, retMsg , retType 0
{
  "key": "163126377342664201"
}
stop
```

:::tip 提示
* API 中成交量设置统一以股为单位。但是牛牛客户端中，A 股是以手为单位展示
* 到价提醒类型，存在最小精度，如下：

    TURNOVER_UP：成交额最小精度为 10 元（人民币元，港元，美元）。传入的数值会自动向下取整到最小精度的整数倍。如果设置【00700成交额102元提醒】，设置后会得到【00700成交额100元提醒】；如果设置【00700 成交额 8 元提醒】，设置后会得到【00700 成交额 0 元提醒】。

    VOLUME_UP：A 股成交量最小精度为 1000 股，其他市场股票成交量最小精度为 10 股。传入的数值会自动向下取整到最小精度的整数倍。

    BID_VOL_UP、ASK_VOL_UP：A 股的买一卖一量最小精度为 100 股。传入的数值会自动向下取整到最小精度的整数倍。

    其余到价提醒类型精度支持到小数点后 3 位
:::

:::tip 接口限制
* 每 30 秒内最多请求 60 次设置到价提醒接口
* 每只股票每种类型可设置的提醒上限是 10 个
:::

---

# 获取到价提醒列表

`GetPriceReminder(req);`

* **介绍**

    获取对指定股票 / 指定市场设置的到价提醒列表

* **参数**

```protobuf
message C2S
{
    //security 和 market 二选一，都存在的情况下 security 优先。
	optional Qot_Common.Security security = 1; // 查询指定股票下的到价提醒
	optional int32 market = 2; //Qot_Common::QotMarket 市场，查询市场下的到价提醒项，不区分沪深
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 市场类型参见 [QotMarket](./quote.md#427)

* **返回**

```protobuf
// 提醒信息列表
message PriceReminderItem
{
    required int64 key = 1; // 每个提醒的唯一标识
	required int32 type = 2; // Qot_Common::PriceReminderType 提醒类型
	required double value = 3; // 提醒参数值
	required string note = 4; // 备注仅支持 20 个以内的中文字符
	required int32 freq = 5; // Qot_Common::PriceReminderFreq 提醒频率类型
	required bool isEnable = 6; // 该提醒设置是否生效。false 不生效，true 生效
}

message PriceReminder
{
	required Qot_Common.Security security = 1; // 股票
	optional string name = 3; // 股票名称
	repeated PriceReminderItem itemList = 2; // 提醒信息列表
}

message S2C
{
	repeated PriceReminder priceReminderList = 1; //到价提醒
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType，返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 提醒类型枚举参见 [PriceReminderType](./quote.md#5160)
>    - 提醒频率枚举参见 [PriceReminderFreq](./quote.md#1059)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetPriceReminder(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功

            const req = {
                c2s: {
                    security: {
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },
                },
            };
            
            websocket.GetPriceReminder(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("PriceReminder: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
PriceReminder: errCode 0, retMsg , retType 0
{
  "priceReminderList": [{
    "security": {
      "market": 1,
      "code": "00700"
    },
    "itemList": [{
      "key": "163126377342664201",
      "type": 1,
      "value": 600,
      "note": "",
      "freq": 1,
      "isEnable": true
    }]
  }]
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 10 次获取到价提醒列表接口
:::

---

# 获取自选股列表

`GetUserSecurity(req);`

* **介绍**

    获取指定分组的自选股列表

* **参数**

```protobuf
message C2S
{
	required string groupName = 1; //分组名，有同名的返回排序首个
}

message Request
{
	required C2S c2s = 1;
}
```

* **返回**

```protobuf
message S2C
{
	repeated Qot_Common.SecurityStaticInfo staticInfoList = 1; //自选股分组下的股票列表
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType，返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 股票静态信息结构参见 [SecurityStaticInfo](./quote.md#609)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetUserSecurity(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功

            const req = {
                c2s: {
                    groupName: "港股",
                },
            };
            
            websocket.GetUserSecurity(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("UserSecurity: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
UserSecurity: errCode 0, retMsg , retType 0
{
  "staticInfoList": [{
    "basic": {
      "security": {
        "market": 1,
        "code": "00700"
      },
      "id": "54047868453564",
      "lotSize": 100,
      "secType": 3,
      "name": "腾讯控股",
      "listTime": "2004-06-16",
      "delisting": false,
      "listTimestamp": 1087315200
    }
  }, {
    "basic": {
      "security": {
        "market": 1,
        "code": "09988"
      },
      "id": "78224239372036",
      "lotSize": 100,
      "secType": 3,
      "name": "阿里巴巴-SW",
      "listTime": "2019-11-26",
      "delisting": false,
      "listTimestamp": 1574697600
    }
  }, {
    "basic": {
      "security": {
        "market": 1,
        "code": "800000"
      },
      "id": "800000",
      "lotSize": 0,
      "secType": 6,
      "name": "恒生指数",
      "listTime": "1970-01-01",
      "delisting": false,
      "listTimestamp": 0
    }
  }]
}
stop
```

:::tip 提示
系统分组的中英文对应名称如下
    
中文|英文
:-|:-|:-
全部|All
沪深|CN
港股|HK
美股|US
期权|Options
港股期权|HK options
美股期权|US options
特别关注|Starred
期货|Futures
:::

:::tip 接口限制
* 每 30 秒内最多请求 10 次获取自选股列表接口
* 不支持持仓（Positions），基金宝（Mutual Fund），外汇（Forex）分组的查询
:::

---

# 获取自选股分组

`GetUserSecurityGroup(req);`

* **介绍**

    获取自选股分组列表

* **参数**

```protobuf
// 自选股的类型
enum GroupType
{
	GroupType_Unknown = 0; // 未知
    GroupType_Custom = 1; // 自定义分组
    GroupType_System = 2; // 系统分组
    GroupType_All = 3; // 全部分组
}

message C2S
{
	required int32 groupType = 1; // GroupType，自选股分组类型。
}

message Request
{
	required C2S c2s = 1;
}
```

* **返回**

```protobuf
// 自选股的类型
enum GroupType
{
	GroupType_Unknown = 0; // 未知
    GroupType_Custom = 1; // 自定义分组
    GroupType_System = 2; // 系统分组
    GroupType_All = 3; // 全部分组
}

message GroupData
{
	required string groupName = 1; // 自选股分组名字
	required int32 groupType = 2; // GroupType，自选股分组类型。
}

message S2C
{
	repeated GroupData groupList = 1; // 自选股分组列表
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType，返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common, Qot_GetUserSecurityGroup } from "futu-api/proto";
import beautify from "js-beautify";

function QotGetUserSecurityGroup(){
    const { RetType } = Common
    const { GroupType } = Qot_GetUserSecurityGroup
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功

            const req = {
                c2s: {
                    groupType: GroupType.GroupType_All,
                },
            };
            
            websocket.GetUserSecurityGroup(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("UserSecurityGroup: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
UserSecurityGroup: errCode 0, retMsg , retType 0
{
  "groupList": [{
    "groupName": "全部",
    "groupType": 2
  }, {
    "groupName": "特别关注",
    "groupType": 2
  }, ..., {
    "groupName": "债券",
    "groupType": 2
  }]
}
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 10 次获取自选股分组接口
:::

---

# 修改自选股列表

`ModifyUserSecurity(req);`

* **介绍**

    修改自选股列表

* **参数**

```protobuf
enum ModifyUserSecurityOp
{
	ModifyUserSecurityOp_Unknown = 0;
	ModifyUserSecurityOp_Add = 1; //新增
	ModifyUserSecurityOp_Del = 2; //删除自选
	ModifyUserSecurityOp_MoveOut = 3; //移出分组
}

message C2S
{
	required string groupName = 1; //分组名，有同名的返回排序的首个
	required int32 op = 2; //ModifyUserSecurityOp，操作类型
	repeated Qot_Common.Security securityList = 3; //新增、删除或移出该分组下的股票
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)

* **返回**

```protobuf
message S2C
{
	
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType，返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common, Qot_ModifyUserSecurity } from "futu-api/proto";
import beautify from "js-beautify";

function QotModifyUserSecurity(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    const { ModifyUserSecurityOp } = Qot_ModifyUserSecurity
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功

            const req = {
                c2s: {
                    groupName: "testgroup",
                    op: ModifyUserSecurityOp.ModifyUserSecurityOp_Add,
                    securityList: [{
                        market: QotMarket.QotMarket_HK_Security,
                        code: "00700",
                    },],
                },
            };

            websocket.ModifyUserSecurity(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("ModifyUserSecurity: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
ModifyUserSecurity: errCode 0, retMsg , retType 0
null
stop
```

:::tip 接口限制
* 每 30 秒内最多请求 10 次修改自选股列表接口
* 仅支持修改自定义分组，不支持修改系统分组
* “全部”自选股列表的数量存在上限：无交易客户 500 个，有交易客户 2000 个（向其他分组增加自选股时，“全部”列表中也会同步增加）
* 如果有同名的分组，会操作排序在第一个的分组
:::

---

# 到价提醒回调

`OnPush(cmd,res)`

* **介绍**

    到价提醒通知回调，异步处理已设置到价提醒的通知推送。

* **参数**

```protobuf
enum MarketStatus
{
	MarketStatus_Unknow = 0;
	MarketStatus_Open = 1; // 盘中
	MarketStatus_USPre = 2;  // 美股盘前
	MarketStatus_USAfter = 3; // 美股盘后
    MarketStatus_USOverNight = 4; // 美股夜盘
}

message S2C
{
	required Qot_Common.Security security = 1; //股票
    optional string name = 11; // 股票名称
	required double price = 2; //价格
	required double changeRate = 3; //当日涨跌幅
	required int32 marketStatus = 4; //Qot_Common::MarketStatus 市场状态
	required string content = 5; //内容
	required string note = 6; //备注仅支持 20 个以内的中文字符
	optional int64 key = 7; //到价提醒的标识
	optional int32 type = 8; //Qot_Common::PriceReminderType，提醒频率类型
	optional double setValue = 9; //设置的提醒值
	optional double curValue = 10; //设置的提醒类型触发时当前值
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType,返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 股票结构参见 [Security](./quote.md#1377)
>    - 提醒类型枚举参见 [PriceReminderType](./quote.md#5160)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common, Trd_Common } from "futu-api/proto";
import beautify from "js-beautify";

function QotUpdatePriceReminder(){
    const { RetType } = Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, 'ec16fde057a2e7a0'];
    let websocket = new ftWebsocket();
    
    // 需要已有设定的到价提醒

    websocket.onPush = (cmd, res)=>{
        if(ftCmdID.QotUpdatePriceReminder.cmd == cmd){ // 到价提醒推送的处理逻辑
            let { retType, s2c } = res
            if(retType == RetType.RetType_Succeed){
                let data = beautify(JSON.stringify(s2c), {
                    indent_size: 2,
                    space_in_empty_paren: true,
                });
                console.log("PriceReminderTest:");
                console.log(data);
            } else {
                console.log("PriceReminderTest: error")
            }
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 3600 * 1000); // 接收 OpenD 的推送持续时间为3600秒, 3600秒后断开
}
```

* **Output**

``` JavaScript
PriceReminderTest:
{
  "security": {
    "market": 1,
    "code": "00700"
  },
  "price": 482.8,
  "changeRate": 1.004,
  "marketStatus": 1,
  "content": "Daily rises more than 1.000%",
  "note": "",
  "key": "163126377342664201",
  "type": 3,
  "setValue": 1,
  "curValue": 1.004
}
stop
```

:::tip 提示
* 此接口提供了持续获取推送数据的功能，如需一次性获取实时数据，请参考 [获取到价提醒](./get-price-reminder.md) 接口
* 获取实时数据 和 实时数据回调 的差别，请参考 [如何通过订阅接口获取实时行情？](../qa/quote.md#2692)
:::

---

# 行情定义

## 累积过滤属性


## 资产类别


## 公司行动


## 暗盘状态


## 财务过滤属性


## 财务过滤属性周期


## 自定义技术指标属性


## 指标语言类型


## 指标搜索模式


## 指标参数值类型


## 指标形状


## 指标线型


## 指标参数值


## 指标输入参数


## 指标输出参数


## 相对位置


## 形态技术指标属性


## 自选股分组类型


## 指数期权类别


## 上市时段


## 窝轮发行商


## K 线字段


## K 线类型


## 周期类型


## 到价提醒市场状态


## 自选股操作


## 期权类型（按行权时间）


## 期权价内/外


## 期权类型（按方向）


## 期权策略类型


## 资讯子类型


## 板块集合类型


## 到价提醒频率


## 到价提醒类型


## 窝轮价内/外


## 逐笔推送类型


## 行情市场


## 市场状态


## 美股时段


## 行情权限


## 关联数据类型


## K 线复权类型


## 股票状态


## 股票类型


## 设置到价提醒操作类型


## 排序方向


## 排序字段


## 排序方式


## 财报类型


## 财报发布时间类型


## 估值类型


## 财务报表类型


## 主营构成维度类型


## 分析师评级


## 研报评级维度类型


## 晨星评级类型


## 估值历史区间类型


## 公司行动重组方式


## 持股变动筛选类型


## 股东持仓明细机构类型


## 公司资料字段类型


## 券商净买卖方向


## 期权波动率查询时间周期


## 期权隐含波动率状态


## 简单过滤属性


## 订阅类型


## 摆盘类型


## 逐笔成交方向


## 逐笔成交类型


## 交易日查询市场


## 交易日类型


## 窝轮状态


## 窝轮类型


## 所属交易所


## 行情公共参数头

**QotHeader**

```protobuf
message QotHeader
{
    optional int32 securityFirm = 1; //券商标识，取值见 Trd_Common.SecurityFirm
}
```

## 证券标识

**Security**

```protobuf
message Security
{
    required int32 market = 1; //QotMarket，行情市场
    required string code = 2; //代码
}
```

## K 线数据

**KLine**

```protobuf
message KLine
{
    required string time = 1; //时间戳字符串（格式：yyyy-MM-dd HH:mm:ss）
    required bool isBlank = 2; //是否是空内容的点,若为 true 则只有时间信息
    optional double highPrice = 3; //最高价
    optional double openPrice = 4; //开盘价
    optional double lowPrice = 5; //最低价
    optional double closePrice = 6; //收盘价
    optional double lastClosePrice = 7; //上一个 K 线的收盘价
    optional int64 volume = 8; //成交量
    optional double turnover = 9; //成交额
    optional double turnoverRate = 10; //换手率（该字段为百分比字段，展示为小数表示）
    optional double pe = 11; //市盈率
    optional double changeRate = 12; //涨跌幅（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
    optional double timestamp = 13; //时间戳
    optional double hpVolume = 14; //高精度成交量
}
```

## 基础报价的期权特有字段

**OptionBasicQotExData**

```protobuf
message OptionBasicQotExData
{
    required double strikePrice = 1; //行权价
    required int32 contractSize = 2; //每份合约数(整型数据)
    optional double contractSizeFloat = 17; //每份合约数（浮点型数据）
    required int32 openInterest = 3; //未平仓合约数
    required double impliedVolatility = 4; //隐含波动率（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
    required double premium = 5; //溢价（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
    required double delta = 6; //希腊值 Delta
    required double gamma = 7; //希腊值 Gamma
    required double vega = 8; //希腊值 Vega
    required double theta = 9; //希腊值 Theta
    required double rho = 10; //希腊值 Rho
    optional int32 netOpenInterest = 11; //净未平仓合约数，仅港股期权适用
    optional int32 expiryDateDistance = 12; //距离到期日天数，负数表示已过期
    optional double contractNominalValue = 13; //合约名义金额，仅港股期权适用
    optional double ownerLotMultiplier = 14; //相等正股手数，指数期权无该字段，仅港股期权适用
    optional int32 optionAreaType = 15; //OptionAreaType，期权类型（按行权时间）
    optional double contractMultiplier = 16; //合约乘数
    optional int32 indexOptionType = 18; //IndexOptionType，指数期权类型
}    
```

## 基础报价的期货特有字段

**FutureBasicQotExData**

```protobuf
message FutureBasicQotExData
{
    required double lastSettlePrice = 1; //昨结
    required int32 position = 2; //持仓量
    required int32 positionChange = 3; //日增仓
    optional int32 expiryDateDistance = 4; //距离到期日天数
}    
```

## 基础报价

**BasicQot**

```protobuf
message BasicQot
{
    required Security security = 1; //股票
    optional string name = 24; // 股票名称
    required bool isSuspended = 2; //是否停牌
    required string listTime = 3; //上市日期字符串（此字段停止维护，不建议使用，格式：yyyy-MM-dd）
    required double priceSpread = 4; //价差
    required string updateTime = 5; //最新价的更新时间字符串（格式：yyyy-MM-dd HH:mm:ss），对其他字段不适用
    required double highPrice = 6; //最高价
    required double openPrice = 7; //开盘价
    required double lowPrice = 8; //最低价
    required double curPrice = 9; //最新价
    required double lastClosePrice = 10; //昨收价
    required int64 volume = 11; //成交量
    required double turnover = 12; //成交额
    required double turnoverRate = 13; //换手率（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
    required double amplitude = 14; //振幅（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
    optional int32 darkStatus = 15; //DarkStatus, 暗盘交易状态	
    optional OptionBasicQotExData optionExData = 16; //期权特有字段
    optional double listTimestamp = 17; //上市日期时间戳（此字段停止维护，不建议使用）
    optional double updateTimestamp = 18; //最新价的更新时间戳，对其他字段不适用
    optional PreAfterMarketData preMarket = 19; //盘前数据
    optional PreAfterMarketData afterMarket = 20; //盘后数据
    optional int32 secStatus = 21; //SecurityStatus, 股票状态
    optional FutureBasicQotExData futureExData = 22; //期货特有字段
    optional double hpVolume = 26; //高精度成交量
}
```

## 盘前盘后数据

**PreAfterMarketData**
 
```protobuf
//美股支持盘前盘后数据
//科创板仅支持盘后数据：成交量，成交额
message PreAfterMarketData
{
    optional double price = 1;  // 盘前或盘后## 价格
    optional double highPrice = 2;  // 盘前或盘后## 最高价
    optional double lowPrice = 3;  // 盘前或盘后## 最低价
    optional int64 volume = 4;  // 盘前或盘后## 成交量
    optional double turnover = 5;  // 盘前或盘后## 成交额
    optional double changeVal = 6;  // 盘前或盘后## 涨跌额
    optional double changeRate = 7;  // 盘前或盘后## 涨跌幅（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
    optional double amplitude = 8;  // 盘前或盘后## 振幅（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
}
```

## 分时数据

**TimeShare**

```protobuf
message TimeShare
{
    required string time = 1; //时间字符串（格式：yyyy-MM-dd HH:mm:ss）
    required int32 minute = 2; //距离0点过了多少分钟
    required bool isBlank = 3; //是否是空内容的点,若为 true 则只有时间信息
    optional double price = 4; //当前价
    optional double lastClosePrice = 5; //昨收价
    optional double avgPrice = 6; //均价
    optional int64 volume = 7; //成交量
    optional double turnover = 8; //成交额
    optional double timestamp = 9; //时间戳
    optional double hpVolume = 10; //高精度成交量
}
```

## 证券基本静态信息

**SecurityStaticBasic**

```protobuf

message SecurityStaticBasic
{
    required Qot_Common.Security security = 1; //股票
    required int64 id = 2; //股票 ID
    required int32 lotSize = 3; //每手数量,期权类型表示一份合约的股数
    required int32 secType = 4; //Qot_Common.SecurityType,股票类型
    required string name = 5; //股票名字
    required string listTime = 6; //上市时间字符串（此字段停止维护，不建议使用，格式：yyyy-MM-dd）
    optional bool delisting = 7; //是否退市
    optional double listTimestamp = 8; //上市时间戳（此字段停止维护，不建议使用）
    optional int32 exchType = 9; //Qot_Common.ExchType,所属交易所
}
```

## 窝轮额外静态信息
**WarrantStaticExData**

```protobuf
message WarrantStaticExData
{
    required int32 type = 1; //Qot_Common.WarrantType,窝轮类型
    required Qot_Common.Security owner = 2; //所属正股
}    
```
## 期权额外静态信息

**OptionStaticExData**

```protobuf
message OptionStaticExData
{
    required int32 type = 1; //Qot_Common.OptionType,期权
    required Qot_Common.Security owner = 2; //标的股
    required string strikeTime = 3; //行权日（格式：yyyy-MM-dd）
    required double strikePrice = 4; //行权价
    required bool suspend = 5; //是否停牌
    required string market = 6; //发行市场名字
    optional double strikeTimestamp = 7; //行权日时间戳
    optional int32 indexOptionType = 8; //Qot_Common.IndexOptionType, 指数期权的类型，仅在指数期权有效
	optional int32 expirationCycle = 9; // ExpirationCycle，交割周期
    optional int32 optionStandardType = 10; // OptionStandardType，标准期权
    optional int32 optionSettlementMode = 11; // OptionSettlementMode，结算方式
}
```

## 期货额外静态信息

**FutureStaticExData**

```protobuf
message FutureStaticExData
{
    required string lastTradeTime = 1; //最后交易日，只有非主连期货合约才有该字段
    optional double lastTradeTimestamp = 2; //最后交易日时间戳，只有非主连期货合约才有该字段
    required bool isMainContract = 3; //是否主连合约
}    
```

## 证券静态信息

**SecurityStaticInfo**

```protobuf
message SecurityStaticInfo
{
    required SecurityStaticBasic basic = 1; //证券基本静态信息
    optional WarrantStaticExData warrantExData = 2; //窝轮额外静态信息
    optional OptionStaticExData optionExData = 3; //期权额外静态信息
    optional FutureStaticExData futureExData = 4; //期货额外静态信息
}
```

## 买卖经纪

**Broker**

```protobuf
message Broker
{
    required int64 id = 1; //经纪 ID
    required string name = 2; //经纪名称
    required int32 pos = 3; //经纪档位
    
    //以下为港股 SF 行情特有字段
    optional int64 orderID = 4; //交易所订单 ID，与交易接口返回的订单 ID 并不一样
    optional int64 volume = 5; //订单股数
}
```

## 逐笔成交

**Ticker**

```protobuf
message Ticker
{
    required string time = 1; //时间字符串（格式：yyyy-MM-dd HH:mm:ss）
    required int64 sequence = 2; // 唯一标识
    required int32 dir = 3; //TickerDirection, 买卖方向
    required double price = 4; //价格
    required int64 volume = 5; //成交量
    required double turnover = 6; //成交额
    optional double recvTime = 7; //收到推送数据的本地时间戳，用于定位延迟
    optional int32 type = 8; //TickerType, 逐笔类型
    optional int32 typeSign = 9; //逐笔类型符号
    optional int32 pushDataType = 10; //用于区分推送情况，仅推送时有该字段
    optional double timestamp = 11; //时间戳
    optional double hpVolume = 12; //高精度成交量
}	
```
## 买卖档明细

**OrderBookDetail**

```protobuf
message OrderBookDetail
{
    required int64 orderID = 1; //交易所订单 ID，与交易接口返回的订单 ID 并不一样
    required int64 volume = 2; //订单股数
}
```

## 买卖档

**OrderBook**

```protobuf
message OrderBook
{
    required double price = 1; //委托价格
    required int64 volume = 2; //委托数量
    required int32 orederCount = 3; //委托订单个数
    repeated OrderBookDetail detailList = 4; //订单信息，港股 SF，美股深度摆盘特有
    optional double hpVolume = 5; //高精度委托数量
}
```

## 持股变动

**ShareHoldingChange**

```protobuf
message ShareHoldingChange
{
    required string holderName = 1; //持有者名称（机构名称 或 基金名称 或 高管姓名）
    required double holdingQty = 2; //当前持股数量
    required double holdingRatio = 3; //当前持股百分比（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
    required double changeQty = 4; //较上一次变动数量
    required double changeRatio = 5; //较上一次变动百分比（该字段为百分比字段，默认不展示 %，如20实际对应20%。是相对于自身的比例，而不是总的。如总股本1万股，持有100股，持股百分比是1%，卖掉50股，变动比例是50%，而不是0.5%）
    required string time = 6; //发布时间（格式：yyyy-MM-dd HH:mm:ss）
    optional double timestamp = 7; //时间戳
}
```

## 单个订阅类型信息

**SubInfo**

```protobuf
message SubInfo
{
    required int32 subType = 1;  //Qot_Common.SubType,订阅类型
    repeated Qot_Common.Security securityList = 2; 	//订阅该类型行情的证券
}	
```

## 单条连接订阅信息

**ConnSubInfo**

```protobuf
message ConnSubInfo
{
    repeated SubInfo subInfoList = 1; //该连接订阅信息
    required int32 usedQuota = 2; //该连接已经使用的订阅额度
    required bool isOwnConnData = 3; //用于区分是否是自己连接的数据
    optional int32 securityFirm = 4; //券商标识，取值见 Trd_Common.SecurityFirm
}
```

## 板块信息

**PlateInfo**

```protobuf
message PlateInfo
{
    required Qot_Common.Security plate = 1; //板块
    required string name = 2; //板块名字
    optional int32 plateType = 3; //PlateSetType 板块类型, 仅3207（获取股票所属板块）协议返回该字段
}
```

## 复权信息

**Rehab**

```protobuf
message Rehab
{
    required string time = 1; //时间字符串（格式：yyyy-MM-dd）
    required int64 companyActFlag = 2; //公司行动(CompanyAct)组合标志位,指定某些字段值是否有效
    required double fwdFactorA = 3; //前复权因子 A
    required double fwdFactorB = 4; //前复权因子 B
    required double bwdFactorA = 5; //后复权因子 A
    required double bwdFactorB = 6; //后复权因子 B
    optional int32 splitBase = 7; //拆股(例如，1拆5，Base 为1，Ert 为5)
    optional int32 splitErt = 8;	
    optional int32 joinBase = 9; //合股(例如，50合1，Base 为50，Ert 为1)
    optional int32 joinErt = 10;	
    optional int32 bonusBase = 11; //送股(例如，10送3, Base 为10,Ert 为3)
    optional int32 bonusErt = 12;	
    optional int32 transferBase = 13; //转赠股(例如，10转3, Base 为10,Ert 为3)
    optional int32 transferErt = 14;	
    optional int32 allotBase = 15; //配股(例如，10送2, 配股价为6.3元, Base 为10, Ert 为2, Price 为6.3)
    optional int32 allotErt = 16;	
    optional double allotPrice = 17;	
    optional int32 addBase = 18; //增发股(例如，10送2, 增发股价为6.3元, Base 为10, Ert 为2, Price 为6.3)
    optional int32 addErt = 19;	
    optional double addPrice = 20;	
    optional double dividend = 21; //现金分红(例如，每10股派现0.5元,则该字段值为0.05)
    optional double spDividend = 22; //特别股息(例如，每10股派特别股息0.5元,则该字段值为0.05)
    optional double timestamp = 23; //时间戳
}
```

> - 公司行动组合标志位参见 [CompanyAct](./quote.html#1239)

## 组合腿信息

**ComboLeg**

```protobuf
message ComboLeg
{
    required Qot_Common.Security security = 1; //股票/期权
    optional int32 side = 2; //方向，取值见 Trd_Common.TrdSide
    optional double qtyRatio = 3; //数量比例
    optional uint64 positionID = 4; //持仓ID，仅 moomoo JP 平仓时填写；须为 showOptionStrategyView=True 时期权策略视图持仓中的 positionID。
}
```

## 交割周期


## 期权标准类型


## 期权结算方式


## 股票持有者（已废弃）


## 筛选 V2 - SimpleField

> 用于 [get_stock_screen](./get-stock-screen.md) 的 `add_simple_field(field, values)` 方法。所有数值字段直接传原始值，OpenD 自动完成倍率转换。

field|含义|values 取值
:-|:-|:-
1|MARKET 市场|ScrMarket：HK=1、US=2、CN=3、SG=4、CA=5、AU=6、JA=7、MY=8
2|EXCHANGE 交易所/上市地|参考 [QotMarket](#427)
3|INDEX_ID 指数 ID|指数成分股 ID
4|USE_WATCHLIST 使用自选股|0=否，1=是
5|HAS_ADR 是否有关联 ADR|0/1
6|HAS_OPTION 是否有期权|0/1
7|HAS_WARRANT 是否有窝轮|0/1
8|HAS_FUTURE 是否有期货|0/1
9|HAS_AH_STOCK 是否有 AH 股|0/1
10|IS_ISLAMIC 回教股|0/1
11|NORTH_BOUND_ID 北向板块|沪/深股通 ID
12|MM_EXCLUSIVE_ID Moomoo 独家板块|板块 ID

> 完整枚举见 SDK 中 `stock_screen_const.py` 的 `SimpleField` / `ScrMarket` 类。

## 筛选 V2 - SimpleProperty

> 用于 `add_simple_property(name, lower, upper)` 与 `add_retrieve_simple(name)`。常用因子如下，所有数值传原始值。

name|含义
:-|:-
2101|LONG_MARGIN_ALLOWED 是否允许融资 (0/1)
2103|SHORT_MARGIN_ALLOWED 是否允许融券 (0/1)
2201|PRICE 最新价
2202|OPEN_PRICE 今开价
2203|LAST_CLOSE 昨收价
2204|HIGH 今高
2205|LOW 今低
2217|VOLUME_RATIO 量比
2218|BID_ASK_RATIO 委比
2301|MARKET_CAP 市值
2302|PE_ANNUAL 静态 PE
2303|PE_TTM TTM 市盈率
2304|PB 市净率
2305|DIVIDEND_RATIO 股息率
2306|LISTED_DATE 上市时间（时间戳）
2307|LISTED_DAYS 上市天数

> 完整枚举见 `SimpleProperty` 类（含融资融券、盘前盘后、夜盘、高精度报价等共 60+ 项）。

## 筛选 V2 - CumulativeProperty

> 用于 `add_cumulative_property(name, days, lower, upper)` 与 `add_retrieve_cumulative(name, days)`。需配合 `days` 参数。

name|含义
:-|:-
3101|PRICE_CHANGE 价格涨跌额
3102|PRICE_CHANGE_PCT 价格涨跌幅 (%)
3103|AMPLITUDE 价格振幅 (%)
3104|AVG_VOLUME 平均成交量
3105|AVG_TURNOVER 平均成交额
3106|TURNOVER_RATIO 换手率 (%)
3107|HIGH_TO_N_DAY_HIGH (今高-N日最高)/N日最高
3108|LOW_TO_N_DAY_LOW (今低-N日最低)/N日最低
3109|PRICE_CHANGE_HP 高精度涨跌额

## 筛选 V2 - FinancialProperty

> 用于 `add_financial_property(name, term, year, lower, upper)` 与 `add_retrieve_financial(name, term, year)`。需配合 `term`（报告期）。

* **常用因子（完整枚举见 `FinancialProperty` 类，含盈利能力 / 偿债 / 运营 / 成长 / 现金流 / 财务超预期等共 100+ 项）**

    name|含义
    :-|:-
    4101|NET_PROFIT 净利润
    4102|NET_PROFIT_GROWTH 净利润增长率
    4105|REVENUE 营业额
    4106|REVENUE_GROWTH 营业额增长率
    4107|NET_PROFIT_RATIO 净利率
    4108|GROSS_PROFIT_RATIO 毛利率
    4109|DEBT_TO_ASSETS 资产负债率
    4110|ROE 净资产收益率
    4202|ROIC 投入资本回报率
    4801|BASIC_EPS 基本每股收益
    4901|TOTAL_SHARE 总股数
    4903|FLOAT_MARKET_CAP 流通市值
    4904|PS_TTM 市销率 TTM
    4905|PCF_TTM 市现率 TTM

* **Term 报告期**（`Term` 枚举）

    term|含义
    :-|:-
    1 / 2 / 3 / 4|Q1 / Q2 / Q3 / Q4 单季报
    6|Q6 中报（累积）
    9|Q9 三季报（累积）
    10|LATEST 最新单季
    100|ANNUAL 年报 FY
    200~204|SURPRISE_LATEST 系列（财报预测）

## 筛选 V2 - Indicator / Pattern / Period / Position

> 用于 `add_indicator_positional` / `add_indicator_pattern` / `add_retrieve_indicator`。

* **`Indicator` 技术指标**（`add_indicator_positional` 的 `first_indicator_name` / `second_indicator`）

    name|含义
    :-|:-
    1|PRICE 最新价
    11~17|MA5 / MA10 / MA20 / MA30 / MA60 / MA120 / MA250
    18|MA 动态简单均线（需设 indicator_params）
    21~27|EMA5 / EMA10 / EMA20 / EMA30 / EMA60 / EMA120 / EMA250
    28|EMA 动态指数均线
    31~33|KDJ_K / KDJ_D / KDJ_J（KDJ(9,3,3)）
    41~43|MACD_DIF / MACD_DEA / MACD_MACD（MACD(12,26,9)）
    51|RSI_12
    52|RSI 动态
    61~63|BOLL_UPPER / BOLL_MIDDLE / BOLL_LOWER（BOLL(20,2)）
    71|RVOL 动态相对成交量

* **`Pattern` 形态**（`add_indicator_pattern` 的 `name`）

    name|含义
    :-|:-
    1 / 2|MA 多头 / 空头排列
    3 / 4|EMA 多头 / 空头排列
    11 / 12|KDJ 低位金叉 / 高位死叉
    13 / 14|KDJ 顶背离 / 底背离
    21 / 22|MACD 低位金叉 / 高位死叉
    23 / 24|MACD 顶背离 / 底背离
    31 / 32|RSI 低位金叉 / 高位死叉
    33 / 34|RSI 顶背离 / 底背离

* **`Period` 周期**

    period|含义
    :-|:-
    1 / 2 / 3 / 4|1 / 3 / 5 / 15 分钟
    5|HOUR_1 1 小时
    6|MINUTE_30 30 分钟
    11 / 21 / 31|DAY 日 / WEEK 周 / MONTH 月

* **`Position` 位置关系**

    position|含义
    :-|:-
    1|OVER first 位于 second 上方
    2|BELOW first 位于 second 下方
    3|CROSS_UP first 上穿 second
    4|CROSS_DOWN first 下穿 second

* **`ScrSortDir` 排序方向**（`set_sort` / `add_sort` 的 `direction`）

    direction|含义
    :-|:-
    1|ASC 升序
    2|DESC 降序
    3|ABS_ASC 绝对值升序
    4|ABS_DESC 绝对值降序

## 筛选 V2 - BasicProperty / 取回字段

> 用于 `add_retrieve_basic(name)` 等取回方法。`add_retrieve_simple` / `add_retrieve_cumulative` / `add_retrieve_financial` 等其余取回字段共用上文 SimpleProperty / CumulativeProperty / FinancialProperty 等 ID。

* **`BasicProperty` 基础属性**

    name|含义|备注
    :-|:-|:-
    1101|CODE 股票代码|sval
    1102|NAME 股票名称|sval
    1103|INDUSTRY 所属行业|sval

> 单条返回结果按 `value_type` 字段分别填入 `sval(1)` / `ival(2)` / `aval(3)` / `dval(4)`。`enum_name` 在 ival 为枚举码时由 SDK 解码（如 K 线形态返回 `'DOUBLE_BOTTOMS'`）。

## 期权筛选 - OptUnderlyingIndicator

> 用于 [get_option_screen](./get-option-screen.md) 的 `add_underlying_filter(indicator_type, ...)` 与 `add_underlying_retrieve(indicator_type)`。

indicator_type|含义|备注
:-|:-|:-
101|STOCK_LIST 指定标的范围|values 直接传入证券代码字符串列表，如 ["US.AAPL", "HK.00700"]
103|PLATE 指定板块|**后台暂不支持，传入会报错**
106|INDEX_LIST 指定指数类型|
201|VOLUME 总成交量|
202|OPEN_INTEREST 总持仓量|
203|IV 标的隐含波动率|
204|HV 标的历史波动率|
205|IV_RANK|
206|IV_PERCENTILE|
207 / 208|IV_CHANGE / IV_CHANGE_RATIO|
209 / 210|IV_HV_RATIO / IV_HV_SPREAD|
401|MARKET_CAP 标的市值|
402|STOCK_PRICE 标的最新价|
403|CHANGE_RATIO 涨跌幅|

## 期权筛选 - OptIndicator

> 用于 `add_option_filter(indicator_type, ...)` 与 `add_option_retrieve(indicator_type)`。

indicator_type|含义|备注
:-|:-|:-
1001|STRIKE_PRICE 行权价|
1002|LEFT_DAY 距到期日天数|
1003|OPTION_TYPE 期权类型|1=CALL，2=PUT
1004|EXERCISE_TYPE 行权方式|1=美式，2=欧式
1005|EXPIRATION_TYPE 到期类型|1=周，2=月，3=季
1007|STRIKE_DATE_TIMESTAMP 到期日时间戳（秒）|
2001|IN_THE_MONEY|0=价外，1=价内
2002~2005|PRICE / MID_PRICE / BID_PRICE / ASK_PRICE|
2006~2009|BID_ASK_SPREAD / BID_VOLUME / ASK_VOLUME / BID_ASK_VOLUME_RATIO|
2010|CHANGE_RATIO 涨跌幅|
2011 / 2012|VOLUME / TURNOVER|
2013 / 2014|OPEN_INTEREST / OPEN_INTEREST_MARKET_CAP|
2018|VOL_OI_RATIO|
2021|PREMIUM 权利金|**仅 sort/retrieve，filter 不支持**
3001 / 3002 / 3003|IMPLIED_VOLATILITY / HISTORY_VOLATILITY / IV_HV_RATIO|
3004~3008|DELTA / GAMMA / VEGA / THETA / RHO|
3009 / 3010|LEVERAGE_RATIO / EFFECTIVE_GEARING|
3011 / 3012|BUY_TO_BEP / SELL_TO_BEP|
3013 / 3014|BUY_PROFIT_PROBABILITY / SELL_PROFIT_PROBABILITY|
3015~3018|INTRINSIC_VALUE_PER / TIME_VALUE_PER / ITM_DEGREE / OTM_DEGREE|
3019 / 3020|ITM_PROBABILITY / OTM_PROBABILITY|

## 窝轮筛选 V2 - WarrantField

> 用于 [get_warrant_screen](./get-warrant-screen.md) 的 `add_interval_filter(field_id, ...)` / `add_choice_filter(field_id, choices)` / `add_sort(field_id, desc)`。所有数值字段直接传原始值。

field_id|含义|筛选方式
:-|:-|:-
1|CODE 证券代码|choice（文本）
2|NAME 股票名称|choice（文本）
4|ISSUER_ID 发行商 ID|choice
5|STOCK_OWNER 正股 ID|choice（可传 "HK.00700"）
6|WARRANT_TYPE 窝轮类型|choice：1=认购，2=认沽，3=牛证，4=熊证，5=界内证
7|CONVERSION_RATIO 换股比率|interval
8|CURRENT_PRICE 当前价|interval
9|STREET_RATIO 街货占比|interval
10|VOLUME 成交量|interval
11|MATURITY_DATE 到期日（时间戳秒）|interval
12|STRIKE_PRICE 行使价|interval
13|PREMIUM 溢价|interval（可为负）
14|RECOVERY_PRICE 收回价|interval
15|IMPLIED_VOLATILITY 引伸波幅|interval
16|LEVERAGE_RATIO 杠杆比率|interval
17|PRICE_RECOVERY_RATIO 正股距收回价 %|interval
18|DELTA 对冲值|interval
19|STATUS 轮证状态|choice：0=正常，1=终止，2=待上市
20|IPO_TIME 上市时间（时间戳秒）|interval
21 / 22|BUY_VOL / SELL_VOL 买/卖量|interval
23|EFFECTIVE_LEVERAGE 有效杠杆|interval
24|LAST_CLOSE_PRICE 昨收价|interval
25|TURNOVER 成交额|interval
26 / 27|SELL_PRICE / BUY_PRICE|interval
28 / 29|HIGH_PRICE / LOW_PRICE|interval
30|RATIO_ITM_OTM 价内/价外|interval（可为负）
31|BREAK_EVEN_POINT 打和点|interval
32|AMPLITUDE 振幅|interval
33|SCORE_FAXING 法兴评分|interval
34|LAST_TRADE_DATE 最后交易日（时间戳秒）|interval
35|STREET_VOLUME 街货量|interval
36|LOT_SIZE 每手股数|interval
37|ISSUE_SIZE 发行量|interval
38|IPO_PRICE 发行价|interval
39 / 40|LOWER_STRIKE_PRICE / UPPER_STRIKE_PRICE|interval（界内证）
41|IW_PRICE_STATUS 界内/界外|choice
42|SENSITIVITY 敏感度|interval
43|CONVERSION_PRICE 换股价|interval
44 / 45|CHANGE_RATE / CHANGE_VALUE 涨跌幅/额|interval
51|SCORE 综合评分|interval
52|FILTER_NO_TRADE 过滤无成交窝轮|choice：0=否，1=是
53|CURRENCY_CODE 币种|choice
54|STOCK_OWNER_PRICE 正股价格|interval

## 窝轮筛选 V2 - WarrantMarket / WarrantType / WarrantStatus

> `WarrantScreenRequest(warrant_market=...)` 与 `add_choice_filter` 常用枚举。

* **`WarrantMarket` 市场**

    market|含义
    :-|:-
    1|HK 港股
    4|SG 新加坡
    15|MY 马来西亚

* **`WarrantType` 窝轮类型**（field_id=6 的 choice 取值）

    value|含义
    :-|:-
    1|CALL 认购
    2|PUT 认沽
    3|BULL 牛证
    4|BEAR 熊证
    5|INLINE 界内证

* **`WarrantStatus` 窝轮状态**（field_id=19 的 choice 取值）

    value|含义
    :-|:-
    0|NORMAL 正常
    1|SUSPEND 终止交易
    2|PRE_IPO 待上市


## 期权市场类型


## 期权统计数据类型


## 历史波动率时间范围


## 期权合约排行类型


## 末日期权标的排序


## 末日期权标的筛选因子


## 末日期权合约排序


## 末日期权合约筛选因子


## 财报排序


## 标的品类


## 财报发布类型


## 财报机会筛选因子


## 卖方策略类型


## 卖方专区排序


## 卖方专区筛选因子


## 标的排行排序


## 标的排行筛选因子


## 期权合约排行筛选因子


## 到期类型


## 指数成分类型


## 期权异动成交方向


## 期权异动订单类型


## 策略类型


## 市场情绪


## 公司行动类型


## 价内价外类型


## 异动筛选因子类型


## 告警操作类型

---

# 交易接口总览

<table>
    <tr>
        <th>模块</th>
        <th>接口名</th>
        <th>功能简介</th>
    </tr>
    <tr>
        <td rowspan="2">账户</td>
	    <td><a href="../trade/get-acc-list.html">GetAccList</a></td>
	    <td>获取交易业务账户列表</td>
    </tr>
    <tr>
	    <td><a href="../trade/unlock.html">UnlockTrade</a></td>
	    <td>解锁交易</td>
    </tr>
    <tr>
        <td rowspan="5">资产持仓</td>
	    <td><a href="../trade/get-funds.html">GetFunds</a></td>
	    <td>获取账户资金数据</td>
    </tr>
    <tr>
	    <td><a href="../trade/get-max-trd-qtys.html">GetMaxTrdQtys</a></td>
	    <td>查询账户下最大可买卖数量</td>
    </tr>
    <tr>
	    <td><a href="../trade/get-position-list.html">GetPositionList</a></td>
	    <td>获取账户持仓列表</td>
    </tr>
    <tr>
	    <td><a href="../trade/get-margin-ratio.html">GetMarginRatio</a></td>
	    <td>获取融资融券数据</td>
    </tr>
    <tr>
        <td><a href="../trade/get-acc-cash-flow.html">FlowSummary</a></td>
	    <td>查询账户资金流水 (最低版本要求：9.1.5108)</td>
    </tr>
    <tr>
        <td rowspan="7">订单</td>
	    <td><a href="../trade/place-order.html">PlaceOrder</a></td>
	    <td>下单</td>
    </tr>
    <tr>
	    <td><a href="../trade/modify-order.html">ModifyOrder</a></td>
	    <td>修改订单</td>
    </tr>
    <tr>
	    <td><a href="../trade/get-order-list.html">GetOrderList</a></td>
	    <td>获取订单列表</td>
    </tr>
	<tr>
	    <td><a href="../trade/order-fee-query.html">GetOrderFee</a></td>
	    <td>获取订单费用 (最低版本要求：8.2.4218)</td>
    </tr>
    <tr>
	    <td><a href="../trade/get-history-order-list.html">GetHistoryOrderList</a></td>
	    <td>获取历史订单列表</td>
    </tr>
    <tr>
	    <td><a href="../trade/update-order.html">UpdateOrder</a></td>
	    <td>订单更新</td>
    </tr>
    <tr>
	    <td><a href="../trade/sub-acc-push.html">SubAccPush</a></td>
	    <td>订阅交易推送</td>
    </tr>
    <tr>
        <td rowspan="3">成交</td>
	    <td><a href="../trade/get-order-fill-list.html">GetOrderFillList</a></td>
	    <td>获取成交列表</td>
    </tr>
    <tr>
	    <td><a href="../trade/get-history-order-fill-list.html">GetHistoryOrderFillList</a></td>
	    <td>获取历史成交列表</td>
    </tr>
    <tr>
	    <td><a href="../trade/update-order-fill.html">OnPush_UpdateOrderFill</a></td>
	    <td>成交更新</td>
    </tr>
</table>

---

# 交易对象

## 创建连接

`start(ip, port, ssl, key)`

* **介绍**

    创建交易对象并初始化交易连接

* **参数**
    参数|类型|说明
    :-|:-|:-
    ip|str|OpenD 监听的 WebSocket 地址
    port|int|OpenD 监听的 WebSocket 端口
    ssl|bool|是否启用 SSL 加密，参见 [WebSocket 相关](../qa/other.html#6319)
    key|str|连接的密钥（未传会出现连接超时），可以在 OpenD 的启动参数中配置。可视化 OpenD 在未配置 WebSocket 密钥的情况下会随机指定

* **Example**

```js
import ftWebSocket from "@/components/ft-websocket/main.js";
class Example {
    example() {
        this.websocket = new ftWebSocket();
        this.websocket.start("127.0.0.1", 33333, false, null);
    }
}
```

## 关闭连接

`close()`  

* **介绍**

    关闭连接

* **Example**

```js
import ftWebSocket from "@/components/ft-websocket/main.js";
class Example {
    example() {
        this.websocket = new ftWebSocket();
        this.websocket.start("127.0.0.1", 33333, false, null);
        this.websocket.close();
    }
}
```

---

# 获取交易业务账户列表

`GetAccList(req);`

* **介绍**

    获取交易业务账户列表

* **参数**

```protobuf
message C2S
{
	required uint64 userID = 1; //历史原因，目前已废弃，填0即可
	optional int32 trdCategory = 2; //交易品类，参考 Trd_Common.TrdCategory
	optional bool needGeneralSecAccount = 3; //是否返回综合账户 （适用于 HK/US/SG/AU 综合账户体系）

message Request
{
	required C2S c2s = 1;
}
```
 
* **返回**

```protobuf
message S2C
{
	repeated Trd_Common.TrdAcc accList = 1; //交易业务账户列表
}

message Response
{
	//以下3个字段每条协议都有，注释说明在 InitConnect.proto 中
	required int32 retType = 1 [default = -400];
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 交易品类 [TrdCategory](./trade.md#6504)
>    - 交易业务账户结构参见 [TrdAcc](./trade.md#8680)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common, Trd_Common } from "futu-api/proto";
import beautify from "js-beautify";

function TrdGetAccList(){
    const { RetType } = Common
    const { SubType, QotMarket } = Qot_Common
    const { TrdCategory } = Trd_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功

            const req = {
                c2s: {
                    userID: 0,
                    trdCategory: TrdCategory.TrdCategory_Security,
                    needGeneralSecAccount: true,
                },
            };
            websocket.GetAccList(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("AccList: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
AccList: errCode 0, retMsg , retType 0
{
  "accList": [{
    "trdEnv": 1,
    "accID": "281756456008357727",
    "trdMarketAuthList": [1],
    "accType": 2,
    "uniCardNum":"1001263856121256",
    "cardNum": "1001100321506782",
    "securityFirm": 1
  }, {
    "trdEnv": 1,
    "accID": "281756460303325023",
    "trdMarketAuthList": [2],
    "accType": 2,
    "uniCardNum":"1001256386562384",
    "cardNum": "1001100521938385",
    "securityFirm": 1
  }, ..., {
    "trdEnv": 0,
    "accID": "6684976",
    "trdMarketAuthList": [2],
    "accType": 2,
    "securityFirm": 0,
    "simAccType": 2
  }]
}
stop
```

---

# 解锁交易

`UnlockTrade(req);`

* **介绍**

    解锁或锁定交易

* **参数**

```protobuf
message C2S
{
        required bool unlock = 1; //true 解锁交易，false 锁定交易
        optional string pwdMD5 = 2; //交易密码的 32 位 MD5 加密（全小写），解锁交易必须要填密码，锁定交易不需要验证密码，可不填
        optional int32 securityFirm = 3; //券商标识，取值见 Trd_Common.SecurityFirm
}

message Request
{
        required C2S c2s = 1;
}
```
>    - 账户所属券商参见 [SecurityFirm](./trade.md#572)

* **返回**

```protobuf
message S2C
{

}

message Response
{
        //以下3个字段每条协议都有，注释说明在 InitConnect.proto 中
        required int32 retType = 1 [default = -400];
        optional string retMsg = 2;
        optional int32 errCode = 3;

        optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common, Trd_Common } from "futu-api/proto";
import beautify from "js-beautify";

function TrdUnlockTrade(){
    const { RetType } = Common
    const { SecurityFirm } = Trd_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功

            const req = {
                c2s: {
                    unlock: true,
                    securityFirm: SecurityFirm.SecurityFirm_FutuSecurities,
                    pwdMD5: "d0970714757783e6cf17b26fb8e2298f", // 设置为自己账号的交易密码MD5
                },
            };
            websocket.UnlockTrade(req)
            .then((res) => {
                let { errCode, retMsg, retType,s2c } = res
                console.log("UnlockTrade: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                if(retType == RetType.RetType_Succeed){
                    let data = beautify(JSON.stringify(s2c), {
                        indent_size: 2,
                        space_in_empty_paren: true,
                    });
                    console.log(data);
                }
            })
            .catch((error) => {
                console.log("error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
UnlockTrade: errCode 0, retMsg , retType 0
null
stop
```

:::tip 提示
* 真实账户调用 [下单](../trade/place-order.md) 或 [改单撤单](../trade/modify-order.md) 接口，需要先解锁交易；模拟账户无需解锁。
* 解锁或锁定交易针是对 OpenD 的操作，只要有一个连接解锁，其他连接都可以调用交易接口。
* 强烈建议，通过外网连接 OpenD 进行实盘交易的客户，使用加密通道，参见 [启用协议加密](../ftapi/init.md#319)。
* 命令行API 不支持富途令牌，如果开通了富途令牌，则会解锁失败，需要关闭令牌功能后再使用 命令行API 解锁。
:::

:::tip 接口限制
* 单用户ID 每 30 秒内最多请求 10 次解锁交易接口
:::

---

# 查询账户资金

`GetFunds(req);`

* **介绍**

    查询交易业务账户的资产净值、证券市值、现金、购买力等资金数据。

* **参数**

```protobuf
message C2S
{
	required Trd_Common.TrdHeader header = 1; //交易公共参数头
	optional bool refreshCache = 2; //立即刷新 OpenD 缓存的此数据，默认不填。true 向服务器获取最新数据更新缓存并返回；flase 或没填则返回 OpenD 缓存的数据，不会向服务器请求。
	//正常情况下，服务器有更新就会立即推送到 OpenD，OpenD 缓存着数据，API 请求过来，返回同步的缓存数据，一般不需要指定刷新缓存，保证快速返回且减少对服务器的压力
	//如果遇到丢包等情况，可能出现缓存数据与服务器不一致，用户如果发现数据更新有异样，可指定刷新缓存，解决数据同步的问题。
	optional int32 currency = 3;	//货币种类，参见 Trd_Common.Currency。期货和综合证券账户必填，其它账户忽略 
	optional int32 assetCategory = 4; //账户资产类型，JP衍生品账户必填，参考 Trd_Common.TrdAssetCategory
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 交易公共参数头结构参见 [TrdHeader](./trade.md#1138)
>    - 货币类型结构参见 [Currency](./trade.md#8019)
>    - 账户资产类型结构参见 [TrdAssetCategory](./trade.md#4752)

* **返回**

```protobuf
message S2C
{
	required Trd_Common.TrdHeader header = 1; //交易公共参数头
	optional Trd_Common.Funds funds = 2; //账户资金
}

message Response
{
	//以下3个字段每条协议都有，注释说明在 InitConnect.proto 中
	required int32 retType = 1 [default = -400];
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 交易公共参数头结构参见 [TrdHeader](./trade.md#1138)
>    - 账户资金结构参见 [Funds](./trade.md#3175)
>    - 持仓限额状态枚举参见 [ExposureLevel](./trade.md#7809)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common, Trd_Common } from "futu-api/proto";
import beautify from "js-beautify";

TrdGetFunds(){
    const { RetType } = Common
    const { TrdEnv, TrdMarket } = Trd_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功
            websocket.GetAccList({
                c2s: {
                    userID: 0,
                },
            }).then((res) => {
                let { retType, s2c: { accList }  } = res
                if(retType == RetType.RetType_Succeed){
                    let acc = accList.filter((item)=>{ 
                        return item.trdEnv == TrdEnv.TrdEnv_Simulate && item.trdMarketAuthList.some((auth)=>{ return auth == TrdMarket.TrdMarket_HK})
                    })[0]; // 样例取第一个香港市场虚拟环境账户

                    const req = {
                        c2s: {
                            header: {
                                trdEnv: acc.trdEnv,
                                accID: acc.accID,
                                trdMarket: TrdMarket.TrdMarket_HK,
                            }
                        },
                    };

                    websocket.GetFunds(req)
                    .then((res) => {
                        let { errCode, retMsg, retType,s2c } = res
                        console.log("GetFunds: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                        if(retType == RetType.RetType_Succeed){
                            let data = beautify(JSON.stringify(s2c), {
                                indent_size: 2,
                                space_in_empty_paren: true,
                            });
                            console.log(data);
                        }
                    })
                    .catch((error) => {
                        console.log("error:", error);
                    });

                }
            })
            .catch((error) => {
                console.log("GetAccList error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
GetFunds: errCode 0, retMsg , retType 0
{
    "header": {
      "trdEnv": 1,
      "accID": "281756455988247915",
      "trdMarket": 1
    },
    "funds": {
        "power": 0.61760332
        "totalAssets": 15222.3336
        "cash": -19.83
        "marketVal": 15242.1666
        "frozenCash": 158.34982707
        "debtCash": 2644.58147475
        "avlWithdrawalCash": 1.24
        "currency": 1
        "initialMargin": 14904.738361057309
        "maintenanceMargin": 14805.9362278707
        "cashInfoList" {
        "currency": 2
        "cash": -95.36
        "availableBalance": 0.0
        "netCashPower": 0.0
        }
        "cashInfoList": {
        "currency": 0
        "cash": 0.0
        "availableBalance": 0.0
        "netCashPower": 0.0
        }
        "cashInfoList": {
        "currency": 1
        "cash": -1097.43
        "availableBalance": 0.0
        "netCashPower": 0.0
        }
        "cashInfoList": {
        "currency": 4
        "cash": -10267.0
        "availableBalance": 0.0
        "netCashPower": 0.0
        }
        "cashInfoList": {
        "currency": 3
        "cash": 2049.58
        "availableBalance": 0.6
        "netCashPower": 0.60345798
        }
        "cashInfoList": {
        "currency": 5
        "cash": 18.62
        "availableBalance": 0.1
        "netCashPower": 0.10953234
        }
        "maxPowerShort": 0.61760332
        "netCashPower": 0.0
        "longMv": 1436.1127
        "shortMv": -168.096
        "pendingAsset": 0.0
        "riskStatus": 3
        "marginCallMargin": 14835.22139711
        "securitiesAssets": 1248.1836
        "fundAssets": 13974.15
        "bondAssets": 0.0
    }
}
stop
```

:::tip 接口限制
* 同一账户ID(acc_id) 每 30 秒内最多请求 10 次查询账户资金接口
* 调用此接口，只有在刷新缓存时，才受到限频限制
:::

---

# 查询最大可买可卖

`GetMaxTrdQtys(req);`

* **介绍**

    查询指定交易业务账户下的最大可买卖数量，亦可查询指定交易业务账户下指定订单的最大可改成的数量。

* **参数**

```protobuf
message C2S
{
	required Trd_Common.TrdHeader header = 1; //交易公共参数头
	required int32 orderType = 2; //订单类型，参见 Trd_Common.OrderType 的枚举定义
	required string code = 3; //代码，港股必须是5位数字，A 股必须是6位数字，美股没限制
	required double price = 4; //价格，（证券账户精确到小数点后 3 位，期货账户精确到小数点后 9 位，超出部分会被舍弃）。如果是竞价、市价单，请也填入一个当前价格，服务器才好计算
	optional uint64 orderID = 5; //订单号，新下订单不需要，如果是修改订单就需要把原订单号带上才行，因为改单的最大买卖数量会包含原订单数量。
	//为保证与下单的价格同步，也提供调整价格选项，以下2个为调整价格使用，对港、A 股有意义，因为港股有价位，A 股2位精度，美股可不传
	optional bool adjustPrice = 6; //是否调整价格，如果价格不合法，是否调整到合法价位，true 调整，false 不调整
	optional double adjustSideAndLimit = 7; //调整方向和调整幅度百分比限制，正数代表向上调整，负数代表向下调整，具体值代表调整幅度限制，如：0.015代表向上调整且幅度不超过1.5%；-0.01代表向下调整且幅度不超过1%
	optional int32 secMarket = 8; //证券所属市场，参见 TrdSecMarket 的枚举定义
	optional string orderIDEx = 9; //表示服务器订单id，可以用来代替orderID，和orderID二选一	
	optional int32 session = 10; //美股订单时段, 参见Common.Session的枚举定义
	optional uint64 positionID = 11; //持仓ID，日本券商查询平仓数量时使用
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 交易公共参数头结构参见 [TrdHeader](./trade.md#1138)
>    - 订单类型结构参见 [OrderType](./trade.md#4181)
>    - 交易证券市场结构参见 [TrdSecMarket](./trade.md#5084)

* **返回**

```protobuf
message S2C
{
	required Trd_Common.TrdHeader header = 1; //交易公共参数头
	optional Trd_Common.MaxTrdQtys maxTrdQtys = 2; //最大可交易数量结构
}

message Response
{
	//以下3个字段每条协议都有，注释说明在 InitConnect.proto 中
	required int32 retType = 1 [default = -400];
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 交易公共参数头结构参见 [TrdHeader](./trade.md#1138)
>    - 最大可交易数量结构参见 [MaxTrdQtys](./trade.md#8065)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common, Trd_Common } from "futu-api/proto";
import beautify from "js-beautify";

function TrdGetMaxTrdQtys(){
    const { RetType } = Common
    const { TrdEnv, OrderType, TrdMarket } = Trd_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功
            websocket.GetAccList({
                c2s: {
                    userID: 0,
                },
            }).then((res) => {
                let { retType, s2c: { accList }  } = res
                if(retType == RetType.RetType_Succeed){
                    let acc = accList.filter((item)=>{ 
                        return item.trdEnv == TrdEnv.TrdEnv_Simulate && item.trdMarketAuthList.some((auth)=>{ return auth == TrdMarket.TrdMarket_HK})
                    })[0]; // 样例取第一个香港市场虚拟环境账户

                    const req = {
                        c2s: {
                            header: {
                                trdEnv: acc.trdEnv,
                                accID: acc.accID,
                                trdMarket: TrdMarket.TrdMarket_HK,
                            },
                            orderType: OrderType.OrderType_Normal,
                            code: "00700", // 指定账号对应市场中的代码
                            price: 100,
                            secMarket: TrdSecMarket.TrdSecMarket_HK,
                        },
                    };

                    websocket.GetMaxTrdQtys(req)
                    .then((res) => {
                        let { errCode, retMsg, retType,s2c } = res
                        console.log("GetMaxTrdQtys: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                        if(retType == RetType.RetType_Succeed){
                            let data = beautify(JSON.stringify(s2c), {
                                indent_size: 2,
                                space_in_empty_paren: true,
                            });
                            console.log(data);
                        }
                    })
                    .catch((error) => {
                        console.log("error:", error);
                    });

                }
            })
            .catch((error) => {
                console.log("GetAccList error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
GetMaxTrdQtys: errCode 0, retMsg , retType 0
{
  "header": {
    "trdEnv": 0,
    "accID": "6684972",
    "trdMarket": 1
  },
  "maxTrdQtys": {
    "maxCashBuy": 1300,
    "maxCashAndMarginBuy": 1300,
    "maxPositionSell": 1900
  }
}
stop
```

:::tip 接口限制
* 同一账户ID(acc_id) 每 30 秒内最多请求 10 次查询最大可买可卖接口
:::

:::tip 提示
* 现金业务账户不支持交易衍生品，因此不支持通过现金业务账户查询期权的最大可买可卖。
* 加密货币仅支持现金账户，因此不支持查询加密货币账户的融资融券购买力。
* 期货的最大可买，需自行计算，公式：floor(最大购买力/买 1 张合约所带来的初始保证金变动)。其中，最大购买力来自[查询账户资金](./get-funds.md)，买 1 张合约所带来的初始保证金变动来自本接口。
:::

---

# 查询组合可交易信息

`GetComboMaxTrdQtys(req);`

* **介绍**

    查询组合订单的可交易信息

* **参数**

```protobuf
message C2S
{
	required Trd_Common.TrdHeader header = 1;
	repeated Qot_Common.ComboLeg comboLegs = 2;
	required double qty = 4;
	optional double price = 5;
	required int32 orderType = 6;
	optional string orderIDEx = 7;
}
```

>    - 交易公共参数头结构参见 [TrdHeader](./trade.md#1138)
>    - 组合腿结构参见 [ComboLeg](./trade.md#1849)

* **返回**

```protobuf
message S2C
{
	required Trd_Common.TrdHeader header = 1;
	optional Trd_Common.ComboMaxTrdQtys maxTrdQtys = 2;
}
```

>    - 组合可交易信息结构参见 [ComboMaxTrdQtys](./trade.md)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

```javascript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common, Trd_Common } from "futu-api/proto";
import beautify from "js-beautify";

function TrdGetComboMaxTrdQtys(){
    const { RetType } = Common
    const { TrdEnv, OrderType, TrdMarket } = Trd_Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功
            websocket.GetAccList({
                c2s: {
                    userID: 0,
                },
            }).then((res) => {
                let { retType, s2c: { accList }  } = res
                if(retType == RetType.RetType_Succeed){
                    let acc = accList.filter((item)=>{ 
                        return item.trdEnv == TrdEnv.TrdEnv_Simulate && item.trdMarketAuthList.some((auth)=>{ return auth == TrdMarket.TrdMarket_US})
                    })[0]; // 样例取第一个美国市场虚拟环境账户

                    const req = {
                        c2s: {
                            header: {
                                trdEnv: acc.trdEnv,
                                accID: acc.accID,
                                trdMarket: TrdMarket.TrdMarket_US,
                            },
                            comboLegs: [
                                {
                                    security: { market: QotMarket.QotMarket_US_Security, code: "AAPL260529C302500" },
                                    side: Trd_Common.TrdSide.TrdSide_Buy,
                                    qtyRatio: 1,
                                },
                                {
                                    security: { market: QotMarket.QotMarket_US_Security, code: "AAPL" },
                                    side: Trd_Common.TrdSide.TrdSide_Sell,
                                    qtyRatio: 100,
                                },
                            ],
                            qty: 1,
                            price: 100,
                            orderType: OrderType.OrderType_Normal,
                        },
                    };

                    websocket.GetComboMaxTrdQtys(req)
                    .then((res) => {
                        let { errCode, retMsg, retType,s2c } = res
                        console.log("GetComboMaxTrdQtys: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                        if(retType == RetType.RetType_Succeed){
                            let data = beautify(JSON.stringify(s2c), {
                                indent_size: 2,
                                space_in_empty_paren: true,
                            });
                            console.log(data);
                        }
                    })
                    .catch((error) => {
                        console.log("error:", error);
                    });

                }
            })
            .catch((error) => {
                console.log("GetAccList error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
GetComboMaxTrdQtys: errCode 0, retMsg , retType 0
{
  "header": {
    "trdEnv": 0,
    "accID": "6684972",
    "trdMarket": 2
  },
  "maxTrdQtys": {
    "nlvChange": -125.3,
    "initialMarginChange": 320.0,
    "maintenanceMarginChange": 300.0,
    "optionBuyPower": 18600.0,
    "maxWithDrawChange": -320.0,
    "buyPowerDecrease": 410.0
  }
}
stop
```

:::tip 接口限制
* 同一账户 ID(acc_id) 每 30 秒内最多请求 10 次查询最大可买可卖类接口。
:::

---

# 查询持仓

`GetPositionList(req);`

* **介绍**

    查询交易业务账户的持仓列表

* **参数**

```protobuf
message C2S
{
	required Trd_Common.TrdHeader header = 1; //交易公共参数头
	optional Trd_Common.TrdFilterConditions filterConditions = 2; //过滤条件
	optional double filterPLRatioMin = 3; //过滤盈亏百分比下限，高于此比例的会返回。证券账户使用摊薄成本价的盈亏比例，期货账户使用平均成本价的盈亏比例
	optional double filterPLRatioMax = 4; //过滤盈亏百分比上限，低于此比例的会返回。证券账户使用摊薄成本价的盈亏比例，期货账户使用平均成本价的盈亏比例
	optional bool refreshCache = 5; //立即刷新 OpenD 缓存的此数据，默认不填。true 向服务器获取最新数据更新缓存并返回；flase 或没填则返回 OpenD 缓存的数据，不会向服务器请求。
	//正常情况下，服务器有更新就会立即推送到 OpenD，OpenD 缓存着数据，API 请求过来，返回同步的缓存数据，一般不需要指定刷新缓存，保证快速返回且减少对服务器的压力
	//如果遇到丢包等情况，可能出现缓存数据与服务器不一致，用户如果发现数据更新有异样，可指定刷新缓存，解决数据同步的问题。
	optional int32 assetCategory = 6; //账户资产类型，JP衍生品账户必填，参考 Trd_Common.TrdAssetCategory
	optional int32 currency = 7; //货币种类，参见 Trd_Common.Currency。加密货币账户必填，其他账户忽略
	optional bool showOptionStrategyView = 8; //是否返回期权策略视图持仓，true 返回策略维度持仓，false 返回标的维度持仓（默认）
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 交易公共参数头结构参见 [TrdHeader](./trade.md#1138)
>    - 过滤条件结构参见 [TrdFilterConditions](./trade.md#3894)
>    - 账户资产类型结构参见 [TrdAssetCategory](./trade.md#4752)
>    - 货币种类参见 [Currency](./trade.md#8019)

* **返回**

```protobuf
message S2C
{
	required Trd_Common.TrdHeader header = 1; //交易公共参数头
	repeated Trd_Common.Position positionList = 2; //持仓列表
}

message Response
{
	//以下3个字段每条协议都有，注释说明在 InitConnect.proto 中
	required int32 retType = 1 [default = -400];
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 交易公共参数头结构参见 [TrdHeader](./trade.md#1138)
>    - 持仓结构参见 [Position](./trade.md#3117)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common, Trd_Common } from "futu-api/proto";
import beautify from "js-beautify";

function TrdGetPositionList(){
    const { RetType } = Common
    const { TrdEnv, TrdMarket } = Trd_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, 'ced92e472b40c92a'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功
            websocket.GetAccList({
                c2s: {
                    userID: 0,
                },
            }).then((res) => {
                let { retType,s2c: { accList } } = res
                if(retType == RetType.RetType_Succeed){
                    let acc = accList.filter((item)=>{ 
                        return item.trdEnv == TrdEnv.TrdEnv_Simulate && item.trdMarketAuthList.some((auth)=>{ return auth == TrdMarket.TrdMarket_HK})
                    })[0]; // 样例取第一个香港市场虚拟环境账户

                    const req = {
                        c2s: {
                            header: {
                                trdEnv: acc.trdEnv,
                                accID: acc.accID,
                                trdMarket: TrdMarket.TrdMarket_HK,
                            },
                        },
                    };

                    websocket.GetPositionList(req)
                    .then((res) => {
                        let { errCode, retMsg, retType,s2c } = res
                        console.log("GetPositionList: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                        if(retType == RetType.RetType_Succeed){
                            let data = beautify(JSON.stringify(s2c), {
                                indent_size: 2,
                                space_in_empty_paren: true,
                            });
                            console.log(data);
                        }
                    })
                    .catch((error) => {
                        console.log("error:", error);
                    });

                }
            })
            .catch((error) => {
                console.log("GetAccList error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
GetPositionList: errCode 0, retMsg , retType 0
{
  "header": {
    "trdEnv": 0,
    "accID": "6684972",
    "trdMarket": 1
  },
  "positionList": [{
    "positionID": "3411713033831199757",
    "positionSide": 0,
    "code": "00700",
    "name": "腾讯控股",
    "qty": 1900,
    "canSellQty": 1900,
    "price": 479.8,
    "costPrice": 454.558,
    "val": 911620,
    "plVal": 47960,
    "plRatio": 0.05553111178009899,
    "secMarket": 1,
    "dilutedCostPrice": 454.558,
    "averageCostPrice": 454.558,
    "averagePlRatio": 0.05553111178009899
  }]
}
stop
```

:::tip 接口限制
* 同一账户ID(acc_id) 每 30 秒内最多请求 10 次查询持仓接口
* 调用此接口，只有在刷新缓存时，才受到限频限制
:::

---

# 获取融资融券数据

`GetMarginRatio(req);`

* **介绍**

    查询股票的融资融券数据。

* **参数**

```protobuf
message C2S
{
	required Trd_Common.TrdHeader header = 1; //交易公共参数头
	repeated Qot_Common.Security securityList = 2; //股票
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 交易公共参数头结构参见 [TrdHeader](./trade.md#1138)
>    - 股票结构参见 [Security](../quote/quote.md#1377)

* **返回**

```protobuf
message MarginRatioInfo
{
	required Qot_Common.Security security = 1; //股票
	optional bool   isLongPermit = 2; //是否允许融资
	optional bool   isShortPermit = 3; //是否允许融券
	optional double shortPoolRemain = 4; //卖空池剩余（股）
	optional double shortFeeRate = 5; //融券参考利率（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
	optional double alertLongRatio = 6; //融资预警比率（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
	optional double alertShortRatio = 7; //融券预警比率（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
	optional double imLongRatio = 8; //融资初始保证金率（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
	optional double imShortRatio = 9; //融券初始保证金率（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
	optional double mcmLongRatio = 10; //融资 margin call 保证金率（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
	optional double mcmShortRatio = 11; //融券 margin call 保证金率（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
	optional double mmLongRatio = 12; //融资维持保证金率（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
	optional double mmShortRatio = 13; //融券维持保证金率（该字段为百分比字段，默认不展示 %，如 20 实际对应 20%）
}

message S2C
{
	required Trd_Common.TrdHeader header = 1; //交易公共参数头
	repeated MarginRatioInfo marginRatioInfoList = 2; //账户资金
}

message Response
{
	//以下3个字段每条协议都有，注释说明 在 InitConnect.proto 中
	required int32 retType = 1 [default = -400];
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 交易公共参数头结构参见 [TrdHeader](./trade.md#1138)
>    - 股票结构参见 [Security](../quote/quote.md#1377)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common, Trd_Common } from "futu-api/proto";
import beautify from "js-beautify";

function TrdGetMarginRatio(){
    const { RetType } = Common
    const { QotMarket } = Qot_Common
    const { TrdEnv, TrdMarket } = Trd_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, 'ced92e472b40c92a'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功
            websocket.GetAccList({
                c2s: {
                    userID: 0,
                },
            }).then((res) => {
                let { retType,s2c: { accList } } = res
                if(retType == RetType.RetType_Succeed){
                    let acc = accList.filter((item)=>{ 
                        return item.trdEnv == TrdEnv.TrdEnv_Simulate && item.trdMarketAuthList.some((auth)=>{ return auth == TrdMarket.TrdMarket_HK})
                    })[0]; // 样例取第一个香港市场虚拟环境账户

                    const req = {
                        c2s: {
                            header: {
                                trdEnv: acc.trdEnv,
                                accID: acc.accID,
                                trdMarket: TrdMarket.TrdMarket_HK,
                            },
                            securityList:[{
                                market: QotMarket.QotMarket_HK_Security,
                                code: "00700",
                            },],
                        },
                    };

                    websocket.GetMarginRatio(req)
                    .then((res) => {
                        let { errCode, retMsg, retType,s2c } = res
                        console.log("GetMarginRatio: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                        if(retType == RetType.RetType_Succeed){
                            let data = beautify(JSON.stringify(s2c), {
                                indent_size: 2,
                                space_in_empty_paren: true,
                            });
                            console.log(data);
                        }
                    })
                    .catch((error) => {
                        console.log("error:", error);
                    });

                }
            })
            .catch((error) => {
                console.log("GetAccList error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
GetMarginRatio: errCode 0, retMsg , retType 0
{
  "header": {
    "trdEnv": 0,
    "accID": "6684972",
    "trdMarket": 1
  },
  "marginRatioInfoList": [{
    "security": {
      "market": 1,
      "code": "00700"
    },
    "isLongPermit": true,
    "isShortPermit": true,
    "shortPoolRemain": 3082200,
    "shortFeeRate": 0.88,
    "alertLongRatio": 33,
    "alertShortRatio": 46,
    "imLongRatio": 35,
    "imShortRatio": 50,
    "mcmLongRatio": 32,
    "mcmShortRatio": 43,
    "mmLongRatio": 25,
    "mmShortRatio": 30
  }]
}
stop
```

:::tip 接口限制
* 单用户ID 每 30 秒内最多请求 10 次获取融资融券数据接口。
* 每次请求，接口参数股票代码列表，支持传入的标的数量上限是 100 个。
* 仅支持港股正股和美股正股的查询。
:::

---

# 查询账户资金流水

`GetAccList(req);`

* **介绍**

    查询交易业务账户在指定日期的资金流水数据。数据覆盖出入金、调拨、货币兑换、买卖金融资产、融资融券利息等所有导致资金变动的事项。

* **参数**

```protobuf
message C2S
{
    required Trd_Common.TrdHeader header = 1; //交易公共参数头
	required string clearingDate = 2; //清算日期，格式 "2017-05-20"
	optional int32 cashFlowDirection = 3; //资金流方向 TrdCashFlowDirection
	optional string startCreateDate = 4; //创建日期开始时间，仅加密货币账户有效，格式 "2017-05-20"
	optional string endCreateDate = 5; //创建日期结束时间，仅加密货币账户有效，格式 "2017-05-20"
}

message Request
{
    required C2S c2s = 1;
}
```
>    - 资金流方向 [TrdCashFlowDirection](./trade.md#7573)
 
* **返回**

```protobuf
message S2C
{
    required Trd_Common.TrdHeader header = 1; //交易公共参数头
	repeated FlowSummaryInfo flowSummaryInfoList = 2; //资金流水数据
}

message Response
{
    //以下3个字段每条协议都有，注释说明在 InitConnect.proto 中
    required int32 retType = 1 [default = -400];
    optional string retMsg = 2;
    optional int32 errCode = 3;
    
    optional S2C s2c = 4;
}
```
>    - 资金流水数据 [FlowSummaryInfo](./trade.md#9378)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common, Trd_Common } from "futu-api/proto";
import beautify from "js-beautify";

function TrdGetFlowSummary(){
    const { RetType } = Common
    const { TrdEnv, OrderType, TrdMarket } = Trd_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功
            websocket.GetAccList({
                c2s: {
                    userID: 0,
                },
            }).then((res) => {
                let { retType, s2c: { accList }  } = res
                if(retType == RetType.RetType_Succeed){
                    let acc = accList.filter((item)=>{ 
                        return item.trdEnv == TrdEnv.TrdEnv_Simulate && item.trdMarketAuthList.some((auth)=>{ return auth == TrdMarket.TrdMarket_HK})
                    })[0]; // 样例取第一个香港市场虚拟环境账户

                    const req = {
                        c2s: {
                            header: {
                                trdEnv: acc.trdEnv,
                                accID: acc.accID,
                                trdMarket: TrdMarket.TrdMarket_HK,
                            },
                            clearingDate: "2025-02-18", 
                        },
                    };

                    websocket.GetFlowSummary(req)
                    .then((res) => {
                        let { errCode, retMsg, retType,s2c } = res
                        console.log("GetFlowSummary: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                        if(retType == RetType.RetType_Succeed){
                            let data = beautify(JSON.stringify(s2c), {
                                indent_size: 2,
                                space_in_empty_paren: true,
                            });
                            console.log(data);
                        }
                    })
                    .catch((error) => {
                        console.log("error:", error);
                    });

                }
            })
            .catch((error) => {
                console.log("GetAccList error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
GetFlowSummary: errCode 0, retMsg , retType 0
{
  "header": {
    "trdEnv": 1,
    "accID": "281756457888247915",
    "trdMarket": 1
  },
  "flowSummaryInfoList": {
    "clearingDate": "2025-02-27",
    "settlementDate": "2025-02-28",
    "currency": 1,
    "cashFlowType": "其他",
    "cashFlowDirection": 1,
    "cashFlowAmount": 23000.00,
    "cashFlowRemark": "Fund Redemption#Taikang Kaitai US Dollar Money",
    "cashFlowID": 16328
  }
}
stop
```

:::tip 接口限制
* 同一账户ID(acc_id) 每 30 秒内最多请求 20 次资金流水接口。  
* 资金流水，按照时间的"顺序"进行排列。  
* 模拟账户不支持查询资金流水。  
:::

---

# 下单

`PlaceOrder(req);`

* **介绍**

    下单

* **参数**

```protobuf

message C2S
{
	required Common.PacketID packetID = 1; //交易写操作防重放攻击
	required Trd_Common.TrdHeader header = 2; //交易公共参数头
	required int32 trdSide = 3; //交易方向，参见 Trd_Common.TrdSide 的枚举定义
	required int32 orderType = 4; //订单类型，参见 Trd_Common.OrderType 的枚举定义
	required string code = 5; //代码，港股必须是5位数字，A 股必须是6位数字，美股没限制
	required double qty = 6; //数量，期权单位是"张"（精确到小数点后 0 位，超出部分会被舍弃。期权期货单位是"张"）
	optional double price = 7; //价格，（证券账户精确到小数点后 3 位，期货账户精确到小数点后 9 位，超出部分会被舍弃）
	//以下2个为调整价格使用，都传才有效，对港、A 股有意义，因为港股有价位，A 股2位精度，美股可不传
	optional bool adjustPrice = 8; //是否调整价格，如果价格不合法，是否调整到合法价位，true 调整，false 不调整。如果价格不合法又不允许调整，则会返回错误
	optional double adjustSideAndLimit = 9; //调整方向和调整幅度百分比限制，正数代表向上调整，负数代表向下调整，具体值代表调整幅度限制，如：0.015代表向上调整且幅度不超过1.5%；-0.01代表向下调整且幅度不超过1%
	optional int32 secMarket = 10; //证券所属市场，参见 TrdSecMarket 的枚举定义
	optional string remark = 11; //用户备注字符串，最多只能传64字节。可用于标识订单唯一信息等，下单填上，订单结构就会带上。
	optional int32 timeInForce = 12; //订单有效期限，参见 TrdCommon.TimeInForce 的枚举定义
	optional bool fillOutsideRTH = 13; //是否允许盘前盘后成交。仅适用于美股限价单。默认 false
	optional double auxPrice = 14; //触发价格
	optional int32 trailType = 15; //跟踪类型, 参见Trd_Common.TrailType的枚举定义
	optional double trailValue = 16; //跟踪金额/百分比
	optional double trailSpread = 17; //指定价差
    optional int32 session = 18; //美股订单时段, 参见Common.Session的枚举定义
	optional uint64 positionID = 19; //持仓ID，JP券商平仓时使用
	optional string expireTime = 20; //订单到期时间，仅在timeInForce为GTD时有效
}

message Request
{
	required C2S c2s = 1;
}
```

> - 请求包标识结构参见 [PacketID](../ftapi/common.md#4068)
> - 交易公共参数头结构参见 [TrdHeader](./trade.md#1138)
> - 交易方向参见 [TrdSide](./trade.md#5815)
> - 订单类型参见 [OrderType](./trade.md#4181)
> - 股票行情市场参见 [TrdSecMarket](./trade.md#5084)
> - 订单有效期参见 [TimeInForce](./trade.md#4241)
> - 跟踪类型参见 [TrailType](./trade.md#5644)

* **返回**
   
```protobuf

message S2C
{
	required Trd_Common.TrdHeader header = 1; //交易公共参数头
	optional uint64 orderID = 2; //订单号
    optional string orderIDEx = 3; //表示服务器订单id，可以用来代替orderID，和orderID二选一		
}

message Response
{
	//以下3个字段每条协议都有，注释说明在 InitConnect.proto 中
	required int32 retType = 1 [default = -400];
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 交易公共参数头结构参见 [TrdHeader](./trade.md#1138)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common, Trd_Common } from "futu-api/proto";
import beautify from "js-beautify";

function TrdPlaceOrder(){
    const { RetType, PacketID } = Common
    const { TrdEnv, TrdSide, OrderType, SecurityFirm, TrdMarket, TrdSecMarket } = Trd_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    let tradeSerialNo = 0;
    websocket.onlogin = async ()=>{
        try{
            let { errCode, retMsg, retType } = await websocket.UnlockTrade({
                c2s: {
                    unlock: true,
                    securityFirm: SecurityFirm.SecurityFirm_FutuSecurities,
                    pwdMD5: "d0970714757783e6cf17b26fb8e2298f", // 设置为自己账号的交易密码MD5
                },
            });
            if(retType == RetType.RetType_Succeed && errCode == 0) { // 解锁交易成功
                let { errCode, retMsg, retType, s2c: { accList } } = await websocket.GetAccList({
                    c2s: {
                        userID: 0,
                    },
                });
                if(retType == RetType.RetType_Succeed && errCode == 0) { // 获取账户成功
                    let acc = accList.filter((item)=>{ 
                        return item.trdEnv == TrdEnv.TrdEnv_Simulate && item.trdMarketAuthList.some((auth)=>{ return auth == TrdMarket.TrdMarket_HK})
                    })[0]; // 样例取第一个香港市场虚拟环境账户
                    
                    const req = {
                        c2s: {
                            packetID:{
                                connID: websocket.getConnID(),
                                serialNo: tradeSerialNo++,
                            },
                            header: {
                                trdEnv: acc.trdEnv,
                                accID: acc.accID,
                                trdMarket: TrdMarket.TrdMarket_HK,
                            },
                            trdSide: TrdSide.TrdSide_Buy,
                            orderType: OrderType.OrderType_Normal,
                            code: "00700",
                            qty: 100,
                            price: 150,
                            secMarket: TrdSecMarket.TrdSecMarket_HK,
                        },
                    };
                    let { errCode, retMsg, retType, s2c } = await websocket.PlaceOrder(req);
                    console.log("PlaceOrder: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                    if(retType == RetType.RetType_Succeed){
                        let data = beautify(JSON.stringify(s2c), {
                            indent_size: 2,
                            space_in_empty_paren: true,
                        });
                        console.log(data);
                    }
                }
            }
        }
        catch(err){
            console.log(err)
        }
        
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
PlaceOrder: errCode 0, retMsg , retType 0
{
  "header": {
    "trdEnv": 0,
    "accID": "6684972",
    "trdMarket": 1
  },
  "orderID": "5870498377428972628"
}
stop
```

:::tip 接口限制
* 同一账户ID(acc_id) 每 30 秒内最多请求 15 次下单接口，且连续两次请求的间隔不可小于 0.02 秒。和[组合下单](place-combo-order.md)共用一个限频。
* 真实账户调用下单接口前，需要先进行 [解锁](./unlock.md)；模拟账户无需解锁。
:::

:::tip 提示
* 各订单类型对应的必传参数：[点击这里](../qa/trade.html#2984) 了解更多
* 各券商针对不同交易品种，对单笔订单股数有所限制，超出限制会导致下单失败：[点击这里](../qa/trade.html#2984) 了解更多
* 对于 **可做空标的**，暂不支持锁仓功能，故无法同时持有相同产品的多头头寸和空头头寸。
* 如果希望对 **可做空标的** 进行 **平仓** 操作，需要自行判断持仓头寸的方向，然后提交一笔反向的相同数量的订单完成平仓操作。
* 如果希望对 **可做空标的** 进行 **反手** 操作，需要两步：1. 先判断持仓头寸的方向，并提交一笔反向的相同数量的订单完成平仓操作；2. 提交一笔反向的订单，完成反向订单的提交。  
举例：A 当前持有 1 手 HK.HSI2012 期货合约的多单，如果希望反手，必须先 卖出 1 手 HK.HSI2012 完成平仓，再卖出 1 手 HK.HSI2012 完成空单的建立。  
* 美股全时段交易，仅支持限价单，订单期限可以选择当日有效或撤单前有效。选择全时段，交易者可以一次挂单参与多个时段（夜盘、盘前、盘中、盘后时段）的交易，全时段交易时间是星期日到星期四 20:00 - 次日20:00（美东时间）  
* 美股模拟交易不支持盘前盘后与夜盘
:::

---

# 组合下单

`PlaceComboOrder(req);`

* **介绍**

    组合期权/组合策略下单

* **参数**

```protobuf
message C2S
{
	required Common.PacketID packetID = 1;
	required Trd_Common.TrdHeader header = 2;
	repeated Qot_Common.ComboLeg comboLegs = 3;
	required double qty = 4;
	optional double price = 5;
	required int32 orderType = 6;
	optional int32 timeInForce = 7;
	optional string expireTime = 8;
	optional string remark = 9;
}
```

* **返回**

```protobuf
message S2C
{
	required Trd_Common.TrdHeader header = 1;
	optional string orderIDEx = 2;
}
```

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common, Trd_Common } from "futu-api/proto";
import beautify from "js-beautify";

function TrdPlaceComboOrder(){
    const { RetType, PacketID } = Common
    const { TrdEnv, TrdSide, OrderType, SecurityFirm, TrdMarket, TimeInForce } = Trd_Common
    const { QotMarket } = Qot_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    let tradeSerialNo = 0;
    websocket.onlogin = async ()=>{
        try{
            let { errCode, retMsg, retType } = await websocket.UnlockTrade({
                c2s: {
                    unlock: true,
                    securityFirm: SecurityFirm.SecurityFirm_FutuSecurities,
                    pwdMD5: "d0970714757783e6cf17b26fb8e2298f", // 设置为自己账号的交易密码MD5
                },
            });
            if(retType == RetType.RetType_Succeed && errCode == 0) { // 解锁交易成功
                let { errCode, retMsg, retType, s2c: { accList } } = await websocket.GetAccList({
                    c2s: {
                        userID: 0,
                    },
                });
                if(retType == RetType.RetType_Succeed && errCode == 0) { // 获取账户成功
                    let acc = accList.filter((item)=>{ 
                        return item.trdEnv == TrdEnv.TrdEnv_Simulate && item.trdMarketAuthList.some((auth)=>{ return auth == TrdMarket.TrdMarket_US})
                    })[0]; // 样例取第一个美国市场虚拟环境账户
                    
                    const req = {
                        c2s: {
                            packetID:{
                                connID: websocket.getConnID(),
                                serialNo: tradeSerialNo++,
                            },
                            header: {
                                trdEnv: acc.trdEnv,
                                accID: acc.accID,
                                trdMarket: TrdMarket.TrdMarket_US,
                            },
                            comboLegs: [
                                {
                                    security: {
                                        market: QotMarket.QotMarket_US_Security,
                                        code: "AAPL260529C302500",
                                    },
                                    side: TrdSide.TrdSide_Buy,
                                    qtyRatio: 1,
                                },
                                {
                                    security: {
                                        market: QotMarket.QotMarket_US_Security,
                                        code: "AAPL",
                                    },
                                    side: TrdSide.TrdSide_Sell,
                                    qtyRatio: 100,
                                },
                            ],
                            qty: 1,
                            price: 9.9,
                            orderType: OrderType.OrderType_Normal,
                            timeInForce: TimeInForce.TimeInForce_DAY,
                            remark: "combo-demo",
                        },
                    };
                    let { errCode, retMsg, retType, s2c } = await websocket.PlaceComboOrder(req);
                    console.log("PlaceComboOrder: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                    if(retType == RetType.RetType_Succeed){
                        let data = beautify(JSON.stringify(s2c), {
                            indent_size: 2,
                            space_in_empty_paren: true,
                        });
                        console.log(data);
                    }
                }
            }
        }
        catch(err){
            console.log(err)
        }
        
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
PlaceComboOrder: errCode 0, retMsg , retType 0
{
  "header": {
    "trdEnv": 0,
    "accID": "6684972",
    "trdMarket": 2
  },
  "orderIDEx": "FH1C79E90941477000"
}
stop
```

:::tip 接口限制
* 同一账户 ID(acc_id) 每 30 秒内最多请求 15 次下单接口，且连续两次请求的间隔不可小于 0.02 秒。和[下单](place-order.md)共用一个限频。
* 真实账户调用下单接口前，需要先进行 [解锁](./unlock.md)；模拟账户无需解锁。
:::

:::tip 提示
* combo_leg_list 中各腿标的须属于同一交易市场，系统将根据第一条腿的市场确定 trd_market。
* 各腿 qty_ratio 与 qty 共同决定每条腿的实际委托数量。
:::

---

# 改单撤单

`ModifyOrder(req);`

* **介绍**

    修改订单的价格和数量、撤单、操作订单的失效和生效、删除订单等。  
	如果是 A 股通市场，将不支持改单。可撤单。删除订单是本地操作。

* **参数**

```protobuf
message C2S
{
	required Common.PacketID packetID = 1; //交易写操作防重放攻击
	required Trd_Common.TrdHeader header = 2; //交易公共参数头
	required uint64 orderID = 3; //订单号，forAll 为 true 时，传0
	required int32 modifyOrderOp = 4; //修改操作类型，参见 Trd_Common.ModifyOrderOp 的枚举定义
	optional bool forAll = 5; //是否对此业务账户的全部订单操作，true：对全部订单，false：对单个订单，不传默认为对单个订单。批量操作仅支持全部撤单，不支持全部生效、全部失效、全部删除。
	
	//下面的字段仅针对单个订单，且 modifyOrderOp 为 ModifyOrderOp_Normal 有效
	optional double qty = 8; //数量，期权单位是"张"（精确到小数点后 0 位，超出部分会被舍弃）
	optional double price = 9; //价格，（证券账户精确到小数点后 3 位，期货账户精确到小数点后 9 位，超出部分会被舍弃）
	//以下为调整价格使用，都传才有效，对港、A 股有意义，因为港股有价位，A 股2位精度，美股可不传
	optional bool adjustPrice = 10; //是否调整价格，如果价格不合法，是否调整到合法价位，true 调整，false 不调整。如果价格不合法又不允许调整，则会返回错误
	optional double adjustSideAndLimit = 11; //调整方向和调整幅度百分比限制，正数代表向上调整，负数代表向下调整，具体值代表调整幅度限制，如：0.015代表向上调整且幅度不超过1.5%；-0.01代表向下调整且幅度不超过1%
	optional double auxPrice = 12; //触发价格
	optional int32 trailType = 13; //跟踪类型, 参见Trd_Common.TrailType的枚举定义
	optional double trailValue = 14; //跟踪金额/百分比
	optional double trailSpread = 15; //指定价差
    optional string orderIDEx = 16; //表示服务器订单id，可以用来代替orderID，和orderID二选一	
}

message Request
{
	required C2S c2s = 1;
}
```
> - 请求包标识结构参见 [PacketID](../ftapi/common.md#4068)
> - 交易公共参数头结构参见 [TrdHeader](./trade.md#1138)
> - 修改操作枚举参见 [ModifyOrderOp](./trade.md#2969)
> - 跟踪类型参见 [TrailType](./trade.md#5644)

* **返回**

```protobuf
message S2C
{
	required Trd_Common.TrdHeader header = 1; //交易公共参数头
	required uint64 orderID = 2; //订单号
    optional string orderIDEx = 3; //服务器订单id	
}

message Response
{
	//以下3个字段每条协议都有，注释说明在 InitConnect.proto 中
	required int32 retType = 1 [default = -400];
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 交易公共参数头结构参见 [TrdHeader](./trade.md#1138)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common, Trd_Common } from "futu-api/proto";
import beautify from "js-beautify";

function TrdModifyOrder(){
    const { RetType, PacketID } = Common
    const { TrdEnv, TrdSide, OrderType, SecurityFirm, TrdMarket, TrdSecMarket, ModifyOrderOp } = Trd_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, '7522027ccf5a06b1'];
    let websocket = new ftWebsocket();

    let tradeSerialNo = 0;
    websocket.onlogin = async ()=>{
        try{
            let { errCode, retMsg, retType } = await websocket.UnlockTrade({
                c2s: {
                    unlock: true,
                    securityFirm: SecurityFirm.SecurityFirm_FutuSecurities,
                    pwdMD5: "d0970714757783e6cf17b26fb8e2298f", // 设置为自己账号的交易密码MD5
                },
            });
            if(retType == RetType.RetType_Succeed && errCode == 0) { // 解锁交易成功
                let { errCode, retMsg, retType, s2c: { accList } } = await websocket.GetAccList({
                    c2s: {
                        userID: 0,
                    },
                });
                if(retType == RetType.RetType_Succeed && errCode == 0) { // 获取账户成功
                    let acc = accList.filter((item)=>{ 
                        return item.trdEnv == TrdEnv.TrdEnv_Simulate && item.trdMarketAuthList.some((auth)=>{ return auth == TrdMarket.TrdMarket_HK})
                    })[0]; // 样例取第一个香港市场虚拟环境账户
                    
                    let { errCode, retMsg, retType, s2c : { orderID } } = await websocket.PlaceOrder({
                        c2s: {
                            packetID:{
                                connID: websocket.getConnID(),
                                serialNo: tradeSerialNo++,
                            },
                            header: {
                                trdEnv: acc.trdEnv,
                                accID: acc.accID,
                                trdMarket: TrdMarket.TrdMarket_HK,
                            },
                            trdSide: TrdSide.TrdSide_Buy,
                            orderType: OrderType.OrderType_Normal,
                            code: "00700",
                            qty: 100,
                            price: 150,
                            secMarket: TrdSecMarket.TrdSecMarket_HK,
                        },
                    }); 
                    if(retType == RetType.RetType_Succeed && errCode == 0){
                        const req = {
                            c2s: {
                                packetID:{
                                    connID: websocket.getConnID(),
                                    serialNo: tradeSerialNo++,
                                },
                                header: {
                                    trdEnv: acc.trdEnv,
                                    accID: acc.accID,
                                    trdMarket: TrdMarket.TrdMarket_HK,
                                },
                                orderID: orderID,
                                modifyOrderOp: ModifyOrderOp.ModifyOrderOp_Normal,
                                qty: 200,
                                price: 100,
                            },
                        };
                        let { errCode, retMsg, retType, s2c } = await websocket.ModifyOrder(req);
                        console.log("ModifyOrder: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                        if(retType == RetType.RetType_Succeed){
                            let data = beautify(JSON.stringify(s2c), {
                                indent_size: 2,
                                space_in_empty_paren: true,
                            });
                            console.log(data);
                        }
                    }
                }
            }
        }
        catch(err){
            console.log(err)
        }
        
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
ModifyOrder: errCode 0, retMsg , retType 0
{
  "header": {
    "trdEnv": 0,
    "accID": "6684972",
    "trdMarket": 1
  },
  "orderID": "5870570404030790740"
}
stop
```

:::tip 接口限制
* 同一账户ID(acc_id) 每 30 秒内最多请求 20 次改单撤单接口，且连续两次请求的间隔不可小于 0.04 秒。  
* 真实账户调用改单撤单接口前，需要先进行 [解锁](./unlock.md)；模拟账户无需解锁。  
:::

:::tip 提示
* 若执行 **修改订单** 操作，各类订单类型对应的必传参数，可 [点击这里](../qa/trade.html#689) 了解更多。
* 如果希望执行 **改单操作** 去 **修改订单数量**，此接口入参的订单数量 **qty**，应该等于期望成交的总数量。  
举例：
一笔订单数量是 N 股，已部分成交 n 股。对于暂未成交的 (N-n) 股，如果您希望撤掉其中的 x 股，**modify_order_op** 应选择 NORMAL，**qty** 应传 (N-x)。
![order_quantity](../img/order_quantity_cn.png)
* 如果希望执行 **撤单操作**，此接口入参的 **modify_order_op** 应该选择 CANCEL。  
举例： 
一笔订单数量是 N 股，已部分成交 n 股。如果希望将未成交的 (N-n) 股全部撤掉，modify_order_op 应选择 CANCEL，此时 qty 和 price 的入参会被忽略。
:::

---

# 查询未完成订单

`GetOrderList(req);`

* **介绍**

    查询指定交易业务账户的未完成订单列表（包含未成交订单、24h内已成交或已撤订单）

* **参数**

```protobuf
message C2S
{
    required Trd_Common.TrdHeader header = 1; //交易公共参数头
    optional Trd_Common.TrdFilterConditions filterConditions = 2; //过滤条件
    repeated int32 filterStatusList = 3; //Trd_Common::OrderStatus，需要过滤的订单状态列表
    optional bool refreshCache = 4; //立即刷新 OpenD 缓存的此数据，默认不填。true 向服务器获取最新数据更新缓存并返回；flase 或没填则返回 OpenD 缓存的数据，不会向服务器请求。
    //正常情况下，服务器有更新就会立即推送到 OpenD，OpenD 缓存着数据，API 请求过来，返回同步的缓存数据，一般不需要指定刷新缓存，保证快速返回且减少对服务器的压力
    //如果遇到丢包等情况，可能出现缓存数据与服务器不一致，用户如果发现数据更新有异样，可指定刷新缓存，解决数据同步的问题。
}

message Request
{
    required C2S c2s = 1;
}
```
>    - 交易公共参数头结构，参见 [TrdHeader](./trade.md#1138)
>    - 订单状态结构，参见 [OrderStatus](./trade.md#797)
>    - 过滤条件结构，参见 [TrdFilterConditions](./trade.md#3894)

* **返回**

```protobuf
message S2C
{
    required Trd_Common.TrdHeader header = 1; //交易公共参数头
    repeated Trd_Common.Order orderList = 2; //订单列表
}

message Response
{
    //以下3个字段每条协议都有，注释说明在 InitConnect.proto 中
    required int32 retType = 1 [default = -400];
    optional string retMsg = 2;
    optional int32 errCode = 3;
    
    optional S2C s2c = 4;
}
```
>    - 交易公共参数头结构，参见 [TrdHeader](./trade.md#1138)
>    - 订单结构，参见 [Order](./trade.md#1935)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common, Trd_Common } from "futu-api/proto";
import beautify from "js-beautify";

function TrdGetOrderList(){
    const { RetType } = Common
    const { TrdEnv, TrdMarket } = Trd_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, 'ec16fde057a2e7a0'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功
            websocket.GetAccList({
                c2s: {
                    userID: 0,
                },
            }).then((res) => {
                let { retType,s2c: { accList } } = res
                if(retType == RetType.RetType_Succeed){
                    let acc = accList.filter((item)=>{ 
                        return item.trdEnv == TrdEnv.TrdEnv_Simulate && item.trdMarketAuthList.some((auth)=>{ return auth == TrdMarket.TrdMarket_HK})
                    })[0]; // 样例取第一个香港市场虚拟环境账户

                    const req = {
                        c2s: {
                            header: {
                                trdEnv: acc.trdEnv,
                                accID: acc.accID,
                                trdMarket: TrdMarket.TrdMarket_HK,
                            },
                        },
                    };

                    websocket.GetOrderList(req)
                    .then((res) => {
                        let { errCode, retMsg, retType,s2c } = res
                        console.log("GetOrderList: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                        if(retType == RetType.RetType_Succeed){
                            let data = beautify(JSON.stringify(s2c), {
                                indent_size: 2,
                                space_in_empty_paren: true,
                            });
                            console.log(data);
                        }
                    })
                    .catch((error) => {
                        console.log("error:", error);
                    });

                }
            })
            .catch((error) => {
                console.log("GetAccList error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
GetOrderList: errCode 0, retMsg , retType 0
{
  "header": {
    "trdEnv": 0,
    "accID": "6378",
    "trdMarket": 1
  },
  "orderList": [{
    "trdSide": 1,
    "orderType": 1,
    "orderStatus": 2,
    "orderID": "6520476875838699625",
    "orderIDEx": "262973",
    "code": "00700",
    "name": "腾讯控股",
    "qty": 100,
    "price": 480,
    "createTime": "2021-09-13 17:07:10",
    "updateTime": "2021-09-13 17:07:10",
    "fillQty": 0,
    "fillAvgPrice": 0,
    "secMarket": 1,
    "createTimestamp": 1631524030,
    "updateTimestamp": 1631524030,
    "remark": "",
    "timeInForce": 0
  }]
}
stop
```

:::tip 接口限制
* 同一账户ID(acc_id) 每 30 秒内最多请求 10 次查询未完成订单接口
* 调用此接口，只有在刷新缓存时，才受到限频限制
:::

:::tip 提示
* 未完成订单，按照时间的”顺序”进行排列，即：先提交的订单在前，后提交的订单在后
:::

---

# 查询历史订单

`GetHistoryOrderList(req);`

* **介绍**

    查询指定交易业务账户的历史订单列表

* **参数**

```protobuf
message C2S
{
	required Trd_Common.TrdHeader header = 1; //交易公共参数头
	required Trd_Common.TrdFilterConditions filterConditions = 2; //过滤条件
	repeated int32 filterStatusList = 3; //Trd_Common::OrderStatus，需要过滤的订单状态列表
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 交易公共参数头结构参见 [TrdHeader](./trade.md#1138)
>    - 过滤条件结构参见 [TrdFilterConditions](./trade.md#3894)
>    - 订单状态枚举参见 [OrderStatus](./trade.md#797)

* **返回**

```protobuf
message S2C
{
	required Trd_Common.TrdHeader header = 1; //交易公共参数头
	repeated Trd_Common.Order orderList = 2; //历史订单列表
}

message Response
{
	//以下3个字段每条协议都有，注释说明在 InitConnect.proto 中
	required int32 retType = 1 [default = -400];
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 交易公共参数头结构参见 [TrdHeader](./trade.md#1138)
>    - 订单结构参见 [Order](./trade.md#1935)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common, Trd_Common } from "futu-api/proto";
import beautify from "js-beautify";

function TrdGetHistoryOrderList(){
    const { RetType } = Common
    const { TrdEnv, TrdMarket } = Trd_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, 'ec16fde057a2e7a0'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功
            websocket.GetAccList({
                c2s: {
                    userID: 0,
                },
            }).then((res) => {
                let { retType,s2c: { accList } } = res
                if(retType == RetType.RetType_Succeed){
                    let acc = accList.filter((item)=>{ 
                        return item.trdEnv == TrdEnv.TrdEnv_Simulate && item.trdMarketAuthList.some((auth)=>{ return auth == TrdMarket.TrdMarket_HK})
                    })[0]; // 样例取第一个香港市场虚拟环境账户

                    const req = {
                        c2s: {
                            header: {
                                trdEnv: acc.trdEnv,
                                accID: acc.accID,
                                trdMarket: TrdMarket.TrdMarket_HK,
                            },
                            filterConditions:{
                                beginTime:"2021-09-01 00:00:00",
                                endTime:"2021-09-30 00:00:00",
                            },
                        },
                    };

                    websocket.GetHistoryOrderList(req)
                    .then((res) => {
                        let { errCode, retMsg, retType,s2c } = res
                        console.log("GetHistoryOrderList: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                        if(retType == RetType.RetType_Succeed){
                            let data = beautify(JSON.stringify(s2c), {
                                indent_size: 2,
                                space_in_empty_paren: true,
                            });
                            console.log(data);
                        }
                    })
                    .catch((error) => {
                        console.log("error:", error);
                    });

                }
            })
            .catch((error) => {
                console.log("GetAccList error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
GetHistoryOrderList: errCode 0, retMsg , retType 0
{
  "header": {
    "trdEnv": 0,
    "accID": "6378",
    "trdMarket": 1
  },
  "orderList": [{
    "trdSide": 1,
    "orderType": 5,
    "orderStatus": 11,
    "orderID": "6520476875838699625",
    "orderIDEx": "262973",
    "code": "00700",
    "name": "腾讯控股",
    "qty": 100,
    "price": 480,
    "createTime": "2021-09-13 17:07:10",
    "updateTime": "2021-09-13 17:07:12",
    "fillQty": 100,
    "fillAvgPrice": 478,
    "secMarket": 1,
    "createTimestamp": 1631524030,
    "updateTimestamp": 1631524032,
    "remark": "",
    "timeInForce": 0
  }]
}
stop
```

:::tip 接口限制
* 同一账户ID(acc_id) 每 30 秒内最多请求 10 次查询历史订单接口
:::

:::tip 提示
* 历史订单，按照时间的“倒序”进行排列，即：后提交的订单在前，先提交的订单在后
:::

---

# 响应订单推送回调

`OnPush(cmd,res)`

* **介绍**

    响应订单推送，异步处理 OpenD 推送过来的订单状态信息。

* **参数**
 
```protobuf
message S2C
{
        required Trd_Common.TrdHeader header = 1; //交易公共参数头
        required Trd_Common.Order order = 2; //订单结构
}

message Response
{
        //以下3个字段每条协议都有，注释说明在 InitConnect.proto 中
        required int32 retType = 1 [default = -400];
        optional string retMsg = 2;
        optional int32 errCode = 3;

        optional S2C s2c = 4;
}
```
>    - 交易公共参数头结构参见 [TrdHeader](./trade.md#1138)
>    - 订单结构参见 [Order](./trade.md#1935)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common, Trd_Common } from "futu-api/proto";
import beautify from "js-beautify";

function TrdUpdateOrder(){
    const { RetType } = Common
    const { TrdEnv, OrderType } = Trd_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, 'ec16fde057a2e7a0'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功
            websocket.GetAccList({
                c2s: {
                    userID: 0,
                },
            }).then((res) => {
                let { retType,s2c: { accList } } = res
                if(retType == RetType.RetType_Succeed){
                    let accIDList = accList.map((acc)=>{ return acc.accID }); // 订阅所有账号的交易推送
                    
                    const req = {
                        c2s: {
                            accIDList: accIDList,
                        },
                    };

                    websocket.SubAccPush(req)
                    .then((res) => {
                        let { errCode, retMsg, retType,s2c } = res
                        console.log("SubAccPush: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                        if(retType == RetType.RetType_Succeed){
                            let data = beautify(JSON.stringify(s2c), {
                                indent_size: 2,
                                space_in_empty_paren: true,
                            });
                            console.log(data);
                        }
                    })
                    .catch((error) => {
                        console.log("error:", error);
                    });

                }
            })
            .catch((error) => {
                console.log("GetAccList error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.onPush = (cmd, res)=>{
        if(ftCmdID.TrdUpdateOrder.cmd == cmd){ // 订单状态变动通知推送的处理逻辑
            let { retType, s2c } = res
            if(retType == RetType.RetType_Succeed){
                let data = beautify(JSON.stringify(s2c), {
                    indent_size: 2,
                    space_in_empty_paren: true,
                });
                console.log("TrdUpdateOrder:");
                console.log(data);
            } else {
                console.log("TrdUpdateOrderTest: error")
            }
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 3600*1000); // 3600秒后断开
}
```

* **Output**

``` JavaScript
SubAccPush: errCode 0, retMsg , retType 0
null
TrdUpdateOrder:
{
  "header": {
    "trdEnv": 1,
    "accID": "281756455988249902",
    "trdMarket": 1
  },
  "order": {
    "trdSide": 1,
    "orderType": 1,
    "orderStatus": 2,
    "orderID": "4883217202603317248",
    "orderIDEx": "20210913_5915950_OD|pM+9NqXZAaxnZYpScrsjT4zHWtlk1",
    "code": "00700",
    "name": "腾讯控股",
    "qty": 100,
    "price": 480,
    "createTime": "2021-09-13 16:45:00",
    "updateTime": "2021-09-13 16:45:00",
    "fillQty": 0,
    "fillAvgPrice": 0,
    "secMarket": 1,
    "createTimestamp": 1631522700,
    "updateTimestamp": 1631522700,
    "remark": "",
    "timeInForce": 0
  }
}
TrdUpdateOrder:
{
  "header": {
    "trdEnv": 1,
    "accID": "281756455988249902",
    "trdMarket": 1
  },
  "order": {
    "trdSide": 1,
    "orderType": 1,
    "orderStatus": 5,
    "orderID": "4883217202603317248",
    "orderIDEx": "20210913_5915950_OD|pM+9NqXZAaxnZYpScrsjT4zHWtlk1",
    "code": "00700",
    "name": "腾讯控股",
    "qty": 100,
    "price": 480,
    "createTime": "2021-09-13 16:45:00.313",
    "updateTime": "2021-09-13 16:45:00.568",
    "fillQty": 0,
    "fillAvgPrice": 0,
    "secMarket": 1,
    "createTimestamp": 1631522700.312849,
    "updateTimestamp": 1631522700.567732,
    "remark": "",
    "timeInForce": 0
  }
}
TrdUpdateOrder:
{
  "header": {
    "trdEnv": 1,
    "accID": "281756455988249902",
    "trdMarket": 1
  },
  "order": {
    "trdSide": 1,
    "orderType": 1,
    "orderStatus": 11,
    "orderID": "4883217202603317248",
    "orderIDEx": "20210913_5915950_OD|pM+9NqXZAaxnZYpScrsjT4zHWtlk1",
    "code": "00700",
    "name": "腾讯控股",
    "qty": 100,
    "price": 480,
    "createTime": "2021-09-13 16:45:00.313",
    "updateTime": "2021-09-13 16:45:00.604",
    "fillQty": 100,
    "fillAvgPrice": 480,
    "secMarket": 1,
    "createTimestamp": 1631522700.312849,
    "updateTimestamp": 1631522700.604215,
    "remark": "",
    "timeInForce": 0
  }
}
stop
```

---

# 查询订单费用

`GetOrderFee(req);`

* **介绍**

    查询指定订单的收费明细（最低版本要求：8.2.4218）

* **参数**

```protobuf
message C2S
{
    required Trd_Common.TrdHeader header = 1; //交易公共参数头
    repeated string orderIdExList = 2; // 服务器订单ID
}

message Request
{
    required C2S c2s = 1;
}
```
>    - 交易公共参数头结构，参见 [TrdHeader](./trade.md#1138)

* **返回**

```protobuf
message S2C
{
    required Trd_Common.TrdHeader header = 1; //交易公共参数头
    repeated Trd_Common.OrderFee orderFeeList = 2; //订单费用列表
}

message Response
{
    //以下3个字段每条协议都有，注释说明在 InitConnect.proto 中
    required int32 retType = 1 [default = -400];
    optional string retMsg = 2;
    optional int32 errCode = 3;
    
    optional S2C s2c = 4;
}
```
>    - 交易公共参数头结构，参见 [TrdHeader](./trade.md#1138)
>    - 订单结构，参见 [OrderFee](./trade.md#1085)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common, Trd_Common } from "futu-api/proto";
import beautify from "js-beautify";

function TrdGetOrderFee(){
    const { RetType } = Common
    const { TrdEnv, TrdMarket } = Trd_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, 'ec16fde057a2e7a0'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功
            websocket.GetAccList({
                c2s: {
                    userID: 0,
                },
            }).then((res) => {
                let { retType,s2c: { accList } } = res
                if(retType == RetType.RetType_Succeed){
                    let acc = accList.filter((item)=>{ 
                        return item.trdEnv != TrdEnv.TrdEnv_Simulate && item.trdMarketAuthList.some((auth)=>{ return auth == TrdMarket.TrdMarket_HK})
                    })[0]; // 样例取第一个香港市场真实环境账户

                    const req = {
                        c2s: {
                            header: {
                                trdEnv: acc.trdEnv,
                                accID: acc.accID,
                                trdMarket: TrdMarket.TrdMarket_HK,
                            },
                            orderIdExList:["6735626686"],
                        },
                    };

                    websocket.GetOrderFee(req)
                    .then((res) => {
                        let { errCode, retMsg, retType,s2c } = res
                        console.log("GetOrderFee: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                        if(retType == RetType.RetType_Succeed){
                            let data = beautify(JSON.stringify(s2c), {
                                indent_size: 2,
                                space_in_empty_paren: true,
                            });
                            console.log(data);
                        }
                    })
                    .catch((error) => {
                        console.log("error:", error);
                    });

                }
            })
            .catch((error) => {
                console.log("GetAccList error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);

    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
GetOrderFee: errCode 0, retMsg , retType 0
{
  "header": {
    "trdEnv": 1,
    "accID": "281756455988249902",
    "trdMarket": 1
  },
  "orderFeeList": [{
    "orderIDEx": "20210913_5915950_OD|pM+9NqXZAaxnZYpScrsjT4zHWtlk1",
    "feeAmount": 522700.6,
    "feeList": [
        {
            "title":"...",
            "value":"...",
        }, ...,{
            "title":"...",
            "value":"...",
        },
    ]
  }, ..., {
    "orderIDEx": "20210913_5915950_OD|rILqM3WaKl2rXYpRYuigcJmBKtRld",
    "feeAmount": 67356.8,
    "feeList": [
        {
            "title":"...",
            "value":"...",
        }, ...,{
            "title":"...",
            "value":"...",
        },
    ]
  }]
}
stop
```

:::tip 接口限制
* 同一账户ID(acc_id) 每 30 秒内最多请求 10 次查询订单费用接口。
* 仅支持查询 2018-01-01 之后的订单。
* 模拟账户不支持查询订单费用。
* 加拿大券商账户不支持查询订单费用。

:::

---

# 订阅交易推送

`SubAccPush(req);`

* **介绍**

    订阅接收交易账户的推送数据  
    指定发送该协议的连接接收交易数据（订单状态，成交状态等）推送

* **参数**

```protobuf
message C2S
{
	repeated uint64 accIDList = 1; //要接收推送数据的业务账号列表，全量非增量，即使用者请每次传需要接收推送数据的所有业务账号
}

message Request
{
	required C2S c2s = 1;
}
```

* **返回**
  
```protobuf
message S2C
{
	
}

message Response
{
	//以下3个字段每条协议都有，注释说明在 InitConnect.proto 中
	required int32 retType = 1 [default = -400];
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common, Trd_Common } from "futu-api/proto";
import beautify from "js-beautify";

function TrdSubAccPush(){
    const { RetType } = Common
    const { TrdEnv, OrderType } = Trd_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, 'ec16fde057a2e7a0'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功
            websocket.GetAccList({
                c2s: {
                    userID: 0,
                },
            }).then((res) => {
                let { retType,s2c: { accList } } = res
                if(retType == RetType.RetType_Succeed){
                    let accIDList = accList.map((acc)=>{ return acc.accID }); // 订阅所有账号的交易推送
                    
                    const req = {
                        c2s: {
                            accIDList: accIDList,
                        },
                    };

                    websocket.SubAccPush(req)
                    .then((res) => {
                        let { errCode, retMsg, retType,s2c } = res
                        console.log("SubAccPush: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                        if(retType == RetType.RetType_Succeed){
                            let data = beautify(JSON.stringify(s2c), {
                                indent_size: 2,
                                space_in_empty_paren: true,
                            });
                            console.log(data);
                        }
                    })
                    .catch((error) => {
                        console.log("error:", error);
                    });

                }
            })
            .catch((error) => {
                console.log("GetAccList error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.onPush = (cmd, res)=>{
        if(ftCmdID.TrdUpdateOrderFill.cmd == cmd){ // 成交通知推送的处理逻辑
            let { retType, s2c } = res
            if(retType == RetType.RetType_Succeed){
                let data = beautify(JSON.stringify(s2c), {
                    indent_size: 2,
                    space_in_empty_paren: true,
                });
                console.log("TrdUpdateOrderFill:");
                console.log(data);
            } else {
                console.log("TrdUpdateOrderFillTest: error")
            }
        } else if(ftCmdID.TrdUpdateOrder.cmd == cmd){ // 订单状态变动通知推送的处理逻辑
            let { retType, s2c } = res
            if(retType == RetType.RetType_Succeed){
                let data = beautify(JSON.stringify(s2c), {
                    indent_size: 2,
                    space_in_empty_paren: true,
                });
                console.log("TrdUpdateOrder:");
                console.log(data);
            } else {
                console.log("TrdUpdateOrderTest: error")
            }
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 3600*1000); // 3600秒后断开
}
```

* **Output**

``` JavaScript
SubAccPush: errCode 0, retMsg , retType 0
null
TrdUpdateOrder:
{
  "header": {
    "trdEnv": 1,
    "accID": "281756455988249902",
    "trdMarket": 1
  },
  "order": {
    "trdSide": 1,
    "orderType": 1,
    "orderStatus": 2,
    "orderID": "4883217202603317248",
    "orderIDEx": "20210913_5915950_OD|pM+9NqXZAaxnZYpScrsjT4zHWtlk1",
    "code": "00700",
    "name": "腾讯控股",
    "qty": 100,
    "price": 480,
    "createTime": "2021-09-13 16:45:00",
    "updateTime": "2021-09-13 16:45:00",
    "fillQty": 0,
    "fillAvgPrice": 0,
    "secMarket": 1,
    "createTimestamp": 1631522700,
    "updateTimestamp": 1631522700,
    "remark": "",
    "timeInForce": 0
  }
}
TrdUpdateOrder:
{
  "header": {
    "trdEnv": 1,
    "accID": "281756455988249902",
    "trdMarket": 1
  },
  "order": {
    "trdSide": 1,
    "orderType": 1,
    "orderStatus": 5,
    "orderID": "4883217202603317248",
    "orderIDEx": "20210913_5915950_OD|pM+9NqXZAaxnZYpScrsjT4zHWtlk1",
    "code": "00700",
    "name": "腾讯控股",
    "qty": 100,
    "price": 480,
    "createTime": "2021-09-13 16:45:00.313",
    "updateTime": "2021-09-13 16:45:00.568",
    "fillQty": 0,
    "fillAvgPrice": 0,
    "secMarket": 1,
    "createTimestamp": 1631522700.312849,
    "updateTimestamp": 1631522700.567732,
    "remark": "",
    "timeInForce": 0
  }
}
TrdUpdateOrder:
{
  "header": {
    "trdEnv": 1,
    "accID": "281756455988249902",
    "trdMarket": 1
  },
  "order": {
    "trdSide": 1,
    "orderType": 1,
    "orderStatus": 11,
    "orderID": "4883217202603317248",
    "orderIDEx": "20210913_5915950_OD|pM+9NqXZAaxnZYpScrsjT4zHWtlk1",
    "code": "00700",
    "name": "腾讯控股",
    "qty": 100,
    "price": 480,
    "createTime": "2021-09-13 16:45:00.313",
    "updateTime": "2021-09-13 16:45:00.604",
    "fillQty": 100,
    "fillAvgPrice": 480,
    "secMarket": 1,
    "createTimestamp": 1631522700.312849,
    "updateTimestamp": 1631522700.604215,
    "remark": "",
    "timeInForce": 0
  }
}
TrdUpdateOrderFill:
{
  "header": {
    "trdEnv": 1,
    "accID": "281756455988249902",
    "trdMarket": 1
  },
  "orderFill": {
    "trdSide": 1,
    "fillID": "932511865781776209",
    "fillIDEx": "20210913_5915950_OD|pM+9NqXZAaxnZYpScrsjT4zHWtlk1_OD|pM+9NqXZAaxnZYpScrsjT4zHWtlk1.2",
    "orderID": "4883217202603317248",
    "orderIDEx": "20210913_5915950_OD|pM+9NqXZAaxnZYpScrsjT4zHWtlk1",
    "code": "00700",
    "name": "腾讯控股",
    "qty": 100,
    "price": 480,
    "createTime": "2021-09-13 16:45:00.606",
    "counterBrokerID": 5,
    "counterBrokerName": "",
    "secMarket": 1,
    "createTimestamp": 1631522700.605828,
    "updateTimestamp": 1631522700.605828,
    "status": 0
  }
}
stop
```

---

# 查询当日成交

`GetOrderFillList(req);`

* **介绍**

    查询指定交易业务账户的当日成交列表。  
    该接口只支持实盘交易，不支持模拟交易。

* **参数**

```protobuf
message C2S
{
	required Trd_Common.TrdHeader header = 1; //交易公共参数头
	optional Trd_Common.TrdFilterConditions filterConditions = 2; //过滤条件
	optional bool refreshCache = 3; //立即刷新 OpenD 缓存的此数据，默认不填。true 向服务器获取最新数据更新缓存并返回；flase 或没填则返回 OpenD 缓存的数据，不会向服务器请求。
	//正常情况下，服务器有更新就会立即推送到 OpenD，OpenD 缓存着数据，API 请求过来，返回同步的缓存数据，一般不需要指定刷新缓存，保证快速返回且减少对服务器的压力
	//如果遇到丢包等情况，可能出现缓存数据与服务器不一致，用户如果发现数据更新有异样，可指定刷新缓存，解决数据同步的问题。
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 交易公共参数头结构参见 [TrdHeader](./trade.md#1138)
>    - 过滤条件结构参见 [TrdFilterConditions](./trade.md#3894)

* **返回**

```protobuf
message S2C
{
	required Trd_Common.TrdHeader header = 1; //交易公共参数头
	repeated Trd_Common.OrderFill orderFillList = 2; //成交列表
}

message Response
{
	//以下3个字段每条协议都有，注释说明在 InitConnect.proto 中
	required int32 retType = 1 [default = -400];
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 交易公共参数头结构参见 [TrdHeader](./trade.md#1138)
>    - 成交结构参见 [OrderFill](./trade.md#1253)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common, Trd_Common } from "futu-api/proto";
import beautify from "js-beautify";

function TrdGetOrderFillList(){
    const { RetType } = Common
    const { TrdEnv, TrdMarket } = Trd_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, 'ec16fde057a2e7a0'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功
            websocket.GetAccList({
                c2s: {
                    userID: 0,
                },
            }).then((res) => {
                let { retType,s2c: { accList } } = res
                if(retType == RetType.RetType_Succeed){
                    let acc = accList.filter((item)=>{ 
                        return item.trdEnv != TrdEnv.TrdEnv_Simulate && item.trdMarketAuthList.some((auth)=>{ return auth == TrdMarket.TrdMarket_HK})
                    })[0]; // 样例取第一个香港市场真实环境账户

                    const req = {
                        c2s: {
                            header: {
                                trdEnv: acc.trdEnv,
                                accID: acc.accID,
                                trdMarket: TrdMarket.TrdMarket_HK,
                            },
                        },
                    };

                    websocket.GetOrderFillList(req)
                    .then((res) => {
                        let { errCode, retMsg, retType,s2c } = res
                        console.log("GetOrderFillList: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                        if(retType == RetType.RetType_Succeed){
                            let data = beautify(JSON.stringify(s2c), {
                                indent_size: 2,
                                space_in_empty_paren: true,
                            });
                            console.log(data);
                        }
                    })
                    .catch((error) => {
                        console.log("error:", error);
                    });

                }
            })
            .catch((error) => {
                console.log("GetAccList error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
GetOrderFillList: errCode 0, retMsg , retType 0
{
  "header": {
    "trdEnv": 1,
    "accID": "281756455988249902",
    "trdMarket": 1
  },
  "orderFillList": [{
    "trdSide": 1,
    "fillID": "2611798069690910040",
    "fillIDEx": "20210913_5915950_OD|rILqM3WaKl2rXYpRYuigcJmBKtRld_OD|rILqM3WaKl2rXYpRYuigcJmBKtRld.2",
    "orderID": "9128832000130556480",
    "orderIDEx": "20210913_5915950_OD|rILqM3WaKl2rXYpRYuigcJmBKtRld",
    "code": "00700",
    "name": "腾讯控股",
    "qty": 100,
    "price": 480,
    "createTime": "2021-09-13 16:40:19.183",
    "counterBrokerID": 5,
    "counterBrokerName": "",
    "secMarket": 1,
    "createTimestamp": 1631522419.18269,
    "updateTimestamp": 1631522419.005,
    "status": 0
  }, {
    "trdSide": 1,
    "fillID": "932511865781776209",
    "fillIDEx": "20210913_5915950_OD|pM+9NqXZAaxnZYpScrsjT4zHWtlk1_OD|pM+9NqXZAaxnZYpScrsjT4zHWtlk1.2",
    "orderID": "4883217202603317248",
    "orderIDEx": "20210913_5915950_OD|pM+9NqXZAaxnZYpScrsjT4zHWtlk1",
    "code": "00700",
    "name": "腾讯控股",
    "qty": 100,
    "price": 480,
    "createTime": "2021-09-13 16:45:00.606",
    "counterBrokerID": 5,
    "counterBrokerName": "",
    "secMarket": 1,
    "createTimestamp": 1631522700.605828,
    "updateTimestamp": 1631522700.531,
    "status": 0
  }]
}
stop
```

:::tip 接口限制
* 同一账户ID(acc_id) 每 30 秒内最多请求 10 次查询当日成交接口
* 调用此接口，只有在刷新缓存时，才受到限频限制
:::

:::tip 提示
* 当日成交，按照时间的“顺序”进行排列，即：先成交的记录在前，后成交的记录在后
:::

---

# 查询历史成交

`GetHistoryOrderFillList(req);`

* **介绍**

    查询指定交易业务账户的历史成交列表。  
    该接口只支持实盘交易，不支持模拟交易。

* **参数**

```protobuf
message C2S
{
	required Trd_Common.TrdHeader header = 1; //交易公共参数头
	required Trd_Common.TrdFilterConditions filterConditions = 2; //过滤条件
}

message Request
{
	required C2S c2s = 1;
}
```
>    - 交易公共参数头结构，参见 [TrdHeader](./trade.md#1138)
>    - 过滤条件结构，参见 [TrdFilterConditions](./trade.md#3894)

* **返回**
 
```protobuf
message S2C
{
	required Trd_Common.TrdHeader header = 1; //交易公共参数头
	repeated Trd_Common.OrderFill orderFillList = 2; //历史成交列表
}

message Response
{
	//以下3个字段每条协议都有，注释说明在 InitConnect.proto 中
	required int32 retType = 1 [default = -400];
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```
>    - 交易公共参数头结构，参见 [TrdHeader](./trade.md#1138)
>    - 成交结构，参见 [OrderFill](./trade.md#1253)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common, Trd_Common } from "futu-api/proto";
import beautify from "js-beautify";

function TrdGetHistoryOrderFillList(){
    const { RetType } = Common
    const { TrdEnv, TrdMarket } = Trd_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, 'ec16fde057a2e7a0'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功
            websocket.GetAccList({
                c2s: {
                    userID: 0,
                },
            }).then((res) => {
                let { retType,s2c: { accList } } = res
                if(retType == RetType.RetType_Succeed){
                    let acc = accList.filter((item)=>{ 
                        return item.trdEnv != TrdEnv.TrdEnv_Simulate && item.trdMarketAuthList.some((auth)=>{ return auth == TrdMarket.TrdMarket_HK})
                    })[0]; // 样例取第一个香港市场真实环境账户

                    const req = {
                        c2s: {
                            header: {
                                trdEnv: acc.trdEnv,
                                accID: acc.accID,
                                trdMarket: TrdMarket.TrdMarket_HK,
                            },
                            filterConditions:{
                                beginTime:"2021-09-01 00:00:00",
                                endTime:"2021-09-30 00:00:00",
                            },
                        },
                    };

                    websocket.GetHistoryOrderFillList(req)
                    .then((res) => {
                        let { errCode, retMsg, retType,s2c } = res
                        console.log("GetHistoryOrderFillList: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                        if(retType == RetType.RetType_Succeed){
                            let data = beautify(JSON.stringify(s2c), {
                                indent_size: 2,
                                space_in_empty_paren: true,
                            });
                            console.log(data);
                        }
                    })
                    .catch((error) => {
                        console.log("error:", error);
                    });

                }
            })
            .catch((error) => {
                console.log("GetAccList error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 5000); // 5秒后断开
}
```

* **Output**

``` JavaScript
GetHistoryOrderFillList: errCode 0, retMsg , retType 0
{
  "header": {
    "trdEnv": 1,
    "accID": "281756455988249902",
    "trdMarket": 1
  },
  "orderFillList": [{
    "trdSide": 1,
    "fillID": "932511865781776209",
    "fillIDEx": "20210913_5915950_OD|pM+9NqXZAaxnZYpScrsjT4zHWtlk1_OD|pM+9NqXZAaxnZYpScrsjT4zHWtlk1.2",
    "orderID": "4883217202603317248",
    "orderIDEx": "20210913_5915950_OD|pM+9NqXZAaxnZYpScrsjT4zHWtlk1",
    "code": "00700",
    "name": "",
    "qty": 100,
    "price": 480,
    "createTime": "2021-09-13 16:45:00.606",
    "counterBrokerID": 5,
    "counterBrokerName": "",
    "secMarket": 1,
    "createTimestamp": 1631522700.605828,
    "updateTimestamp": 1631522700.531,
    "status": 0
  }, {
    "trdSide": 1,
    "fillID": "2611798069690910040",
    "fillIDEx": "20210913_5915950_OD|rILqM3WaKl2rXYpRYuigcJmBKtRld_OD|rILqM3WaKl2rXYpRYuigcJmBKtRld.2",
    "orderID": "9128832000130556480",
    "orderIDEx": "20210913_5915950_OD|rILqM3WaKl2rXYpRYuigcJmBKtRld",
    "code": "00700",
    "name": "",
    "qty": 100,
    "price": 480,
    "createTime": "2021-09-13 16:40:19.183",
    "counterBrokerID": 5,
    "counterBrokerName": "",
    "secMarket": 1,
    "createTimestamp": 1631522419.18269,
    "updateTimestamp": 1631522419.005,
    "status": 0
  }]
}
stop
```

:::tip 接口限制
* 同一账户ID(acc_id) 每 30 秒内最多请求 10 次查询历史成交接口
:::

:::tip 提示
* 历史成交，按照时间的“倒序”进行排列，即：后成交的记录在前，先成交的记录在后
:::

---

# 响应成交推送回调

`OnPush(cmd,res)`

* **介绍**

    响应成交推送，异步处理 OpenD 推送过来的成交状态信息。  
    该接口只支持实盘交易，不支持模拟交易。

* **参数**

```protobuf
message S2C
{
        required Trd_Common.TrdHeader header = 1; //交易公共参数头
        required Trd_Common.OrderFill orderFill = 2; //成交结构
}

message Response
{
        //以下3个字段每条协议都有，注释说明在 InitConnect.proto 中
        required int32 retType = 1 [default = -400];
        optional string retMsg = 2;
        optional int32 errCode = 3;

        optional S2C s2c = 4;
}
```
>    - 交易公共参数头结构参见 [TrdHeader](./trade.md#1138)
>    - 成交结构参见 [OrderFill](./trade.md#1253)
>    - 接口调用结果，结构参见 [RetType](../ftapi/common.html#7467)

* **Example**

``` JavaScript
import ftWebsocket from "futu-api";
import { ftCmdID } from "futu-api";
import { Common, Qot_Common, Trd_Common } from "futu-api/proto";
import beautify from "js-beautify";

function TrdUpdateOrderFill(){
    const { RetType } = Common
    const { TrdEnv, OrderType } = Trd_Common
    let [addr, port, enable_ssl, key] = ["127.0.0.1", 33333, false, 'ec16fde057a2e7a0'];
    let websocket = new ftWebsocket();

    websocket.onlogin = (ret, msg)=>{
        if (ret) { // 登录成功
            websocket.GetAccList({
                c2s: {
                    userID: 0,
                },
            }).then((res) => {
                let { retType,s2c: { accList } } = res
                if(retType == RetType.RetType_Succeed){
                    let accIDList = accList.map((acc)=>{ return acc.accID }); // 订阅所有账号的交易推送
                    
                    const req = {
                        c2s: {
                            accIDList: accIDList,
                        },
                    };

                    websocket.SubAccPush(req)
                    .then((res) => {
                        let { errCode, retMsg, retType,s2c } = res
                        console.log("SubAccPush: errCode %d, retMsg %s, retType %d", errCode, retMsg, retType); 
                        if(retType == RetType.RetType_Succeed){
                            let data = beautify(JSON.stringify(s2c), {
                                indent_size: 2,
                                space_in_empty_paren: true,
                            });
                            console.log(data);
                        }
                    })
                    .catch((error) => {
                        console.log("error:", error);
                    });

                }
            })
            .catch((error) => {
                console.log("GetAccList error:", error);
            });
        } else {
            console.log("error", msg);
        }
    };

    websocket.onPush = (cmd, res)=>{
        if(ftCmdID.TrdUpdateOrderFill.cmd == cmd){ // 成交通知推送的处理逻辑
            let { retType, s2c } = res
            if(retType == RetType.RetType_Succeed){
                let data = beautify(JSON.stringify(s2c), {
                    indent_size: 2,
                    space_in_empty_paren: true,
                });
                console.log("TrdUpdateOrderFill:");
                console.log(data);
            } else {
                console.log("TrdUpdateOrderFillTest: error")
            }
        }
    };

    websocket.start(addr, port, enable_ssl, key);
    
    //关闭行情连接，连接不再使用之后，要关闭，否则占用不必要资源
    //同时OpenD也限制了最多128条连接
    //也可以一个页面或者一个项目维护一条连接，这里范例请求一次创建一条连接
    setTimeout(()=>{ 
        websocket.stop();
        console.log("stop");
    }, 3600*1000); // 3600秒后断开
}
```

* **Output**

``` JavaScript
SubAccPush: errCode 0, retMsg , retType 0
null
TrdUpdateOrderFill:
{
  "header": {
    "trdEnv": 1,
    "accID": "281756455988249902",
    "trdMarket": 1
  },
  "orderFill": {
    "trdSide": 1,
    "fillID": "932511865781776209",
    "fillIDEx": "20210913_5915950_OD|pM+9NqXZAaxnZYpScrsjT4zHWtlk1_OD|pM+9NqXZAaxnZYpScrsjT4zHWtlk1.2",
    "orderID": "4883217202603317248",
    "orderIDEx": "20210913_5915950_OD|pM+9NqXZAaxnZYpScrsjT4zHWtlk1",
    "code": "00700",
    "name": "腾讯控股",
    "qty": 100,
    "price": 480,
    "createTime": "2021-09-13 16:45:00.606",
    "counterBrokerID": 5,
    "counterBrokerName": "",
    "secMarket": 1,
    "createTimestamp": 1631522700.605828,
    "updateTimestamp": 1631522700.605828,
    "status": 0
  }
}
stop
```

---

# 交易定义

## 账户风控状态

**CltRiskLevel**

```protobuf
enum CltRiskLevel
{
    CltRiskLevel_Unknown = -1;        // 未知
    CltRiskLevel_Safe = 0;          // 安全
    CltRiskLevel_Warning = 1;       // 预警
    CltRiskLevel_Danger = 2;        // 危险
    CltRiskLevel_AbsoluteSafe = 3;  // 绝对安全
    CltRiskLevel_OptDanger = 4;     // 危险（期权相关）
}
```

## 货币类型

**Currency**

```protobuf
enum Currency
{
    Currency_Unknown = 0;  //未知货币
    Currency_HKD = 1;   // 港元
    Currency_USD = 2;   // 美元
    Currency_CNH = 3;   // 离岸人民币
    Currency_JPY = 4;   // 日元
    Currency_SGD = 5;   // 新元
	  Currency_AUD = 6;   // 澳元、
    Currency_CAD = 7; // 加拿大元
    Currency_MYR = 8; // 马来西亚林吉特
}
```

## 跟踪类型

```protobuf
enum TrailType
{
	TrailType_Unknown = 0; //未知类型
	TrailType_Ratio = 1; //比例
	TrailType_Amount = 2; //金额
}
```

## 修改订单操作

**ModifyOrderOp**

```protobuf
enum ModifyOrderOp
{
    //港股支持全部操作，美股目前仅支持 ModifyOrderOp_Normal 和 ModifyOrderOp_Cancel
    ModifyOrderOp_Unknown = 0; //未知操作
    ModifyOrderOp_Normal = 1; //修改订单的价格、数量，即以前的改单
    ModifyOrderOp_Cancel = 2; //撤单。未成交订单将直接从交易所撮合队列中撤销。
    ModifyOrderOp_Disable = 3; //使失效。对交易所来说，「失效」的效果等同于 「撤单」。订单「失效」后，未成交订单将直接从交易所撮合队列中撤出，但订单信息（如价格和数量）会继续保留在富途服务器，您随时可以重新使它生效。
    ModifyOrderOp_Enable = 4; //使生效。对交易所来说，「生效」等同于下一笔新订单。订单重新「生效」后，将按照原来的价格数量重新提交到交易所，并按照价格优先、时间优先顺序重新排队。
    ModifyOrderOp_Delete = 5; //删除。指对已撤单/下单失败的订单进行隐藏操作。
}
```

## 成交状态

**OrderFillStatus**

```protobuf
enum OrderFillStatus
{
    OrderFillStatus_OK = 0; //正常
    OrderFillStatus_Cancelled = 1; //成交被取消
    OrderFillStatus_Changed = 2; //成交被更改
}
```

## 订单状态

**OrderStatus**

```protobuf
enum OrderStatus
{
    OrderStatus_Unknown = -1; //未知状态
    OrderStatus_WaitingSubmit = 1; //等待提交
    OrderStatus_Submitting = 2; //提交中
    OrderStatus_Submitted = 5; //已提交，等待成交
    OrderStatus_Filled_Part = 10; //部分成交
    OrderStatus_Filled_All = 11; //全部已成
    OrderStatus_Cancelled_Part = 14; //部分成交，剩余部分已撤单
    OrderStatus_Cancelled_All = 15; //全部已撤单，无成交
    OrderStatus_Failed = 21; //下单失败，服务拒绝
    OrderStatus_Disabled = 22; //已失效
    OrderStatus_Deleted = 23; //已删除，无成交的订单才能删除
    OrderStatus_FillCancelled = 24; //成交被撤销（一般遇不到，意思是已经成交的订单被回滚撤销，成交无效变为废单）
};
```

## 订单类型

:::tip 提示
* [实盘交易中，各个品类支持的订单类型](../qa/trade.md#2731)
* 模拟交易中，仅支持限价单(NORMAL)和市价单(MARKET)。
:::

**OrderType**

```protobuf
enum OrderType
{
    OrderType_Unknown = 0; //未知类型
    OrderType_Normal = 1; //限价单
    OrderType_Market = 2; //市价单
    OrderType_AbsoluteLimit = 5; //绝对限价订单（仅港股），只有价格完全匹配才成交，否则下单失败。举例：下一笔价格为 5 元的绝对限价买单，卖方的价格必须也是5元才能成交，卖方即使低于 5 元也不能成交，下单失败。卖出同理
    OrderType_Auction = 6; //竞价订单（仅港股），仅港股早盘竞价和收盘竞价有效
    OrderType_AuctionLimit = 7; //竞价限价订单（仅港股），仅早盘竞价和收盘竞价有效，参与竞价，且要求满足指定价格才会成交
    OrderType_SpecialLimit = 8; //特别限价订单（仅港股），成交规则同增强限价订单，且部分成交后，交易所自动撤销订单
    OrderType_SpecialLimit_All = 9; //特别限价且要求全部成交订单（仅港股）。全部成交，否则自动撤单
    OrderType_Stop = 10; // 止损市价单
    OrderType_StopLimit = 11; // 止损限价单
    OrderType_MarketifTouched = 12; // 触及市价单（止盈）
    OrderType_LimitifTouched = 13; // 触及限价单（止盈）
    OrderType_TrailingStop = 14; // 跟踪止损市价单
    OrderType_TrailingStopLimit = 15; // 跟踪止损限价单
    OrderType_TWAP  = 16; // 时间加权市价算法单（仅美股）
    OrderType_TWAP_LIMIT = 17; // 时间加权限价算法单 （港股和美股）
    OrderType_VWAP  = 18; // 成交量加权市价算法单（仅美股）
    OrderType_VWAP_LIMIT  = 19; // 成交量加权限价算法单（港股和美股）
}
```

## 持仓方向

**PositionSide**

```protobuf
enum PositionSide
{
    PositionSide_Long = 0; //多仓，默认情况是多仓
    PositionSide_Unknown = -1; //未知方向
    PositionSide_Short = 1; //空仓
};
```

## 期权组合持仓类型

**PositionType**

```protobuf
enum PositionType
{
    PositionType_Unknown = 0;  //未知
    PositionType_Combined = 1; //组合汇总持仓
    PositionType_Leg = 2;      //单腿持仓
};
```

## 账户类型

**TrdAccType**

```protobuf
enum TrdAccType
{
    TrdAccType_Unknown = 0; //未知类型
    TrdAccType_Cash = 1;    //现金账户
    TrdAccType_Margin = 2;  //保证金账户
    TrdAccType_TFSA = 3;    //加拿大免税账户
    TrdAccType_RRSP = 4;    //加拿大注册退休账户
    TrdAccType_SRRSP = 5;    //加拿大配偶退休账户
    TrdAccType_Derivatives = 6;    //日本衍生品账户
};
```

## 交易环境

**TrdEnv**

```protobuf
enum TrdEnv
{
    TrdEnv_Simulate = 0; //模拟环境
    TrdEnv_Real = 1; //真实环境
}
```

## 交易市场

**TrdMarket**

```protobuf
enum TrdMarket
{
    TrdMarket_Unknown = 0; //未知市场
    TrdMarket_HK = 1; //香港市场（证券、期权）
    TrdMarket_US = 2; //美国市场（证券、期权）
    TrdMarket_CN = 3; //A 股市场（仅用于模拟交易）
    TrdMarket_HKCC = 4; //A 股通市场（股票）
    TrdMarket_Futures = 5; //期货市场（环球期货）
    TrdMarket_SG = 6; //新加坡市场
    TrdMarket_Crypto = 7; //加密货币市场
    TrdMarket_AU = 8; //澳洲市场
    TrdMarket_Futures_Simulate_HK = 10; //香港期货模拟市场
    TrdMarket_Futures_Simulate_US = 11; //美国期货模拟市场
    TrdMarket_Futures_Simulate_SG = 12; //新加坡期货模拟市场
    TrdMarket_Futures_Simulate_JP = 13; //日本期货模拟市场
    TrdMarket_JP = 15; //日本市场
    TrdMarket_MY = 111; //马来西亚市场
    TrdMarket_CA = 112; //加拿大市场
    TrdMarket_HK_Fund = 113; //香港基金市场
    TrdMarket_US_Fund = 123; //美国基金市场
    TrdMarket_SG_Fund = 124; //新加坡基金市场
    TrdMarket_MY_Fund = 125; //马来西亚基金市场
    TrdMarket_JP_Fund = 126; //日本基金市场
}
```


## 账户状态

**TrdAccStatus**

```protobuf
enum TrdAccStatus
{
    TrdAccStatus_Active = 0; //生效账户
    TrdAccStatus_Disabled = 1; //失效账户
}
```


## 账户结构

**TrdAccRole**

```protobuf
enum TrdAccRole
{
    TrdAccRole_Unknown = 0; //未知
    TrdAccRole_Normal = 1; //普通账户
    TrdAccRole_Master = 2; //主账户
    TrdAccRole_IPO = 3; //马来西亚IPO账户
}
```


## 交易证券市场

**TrdSecMarket**

```protobuf
enum TrdSecMarket
{
    TrdSecMarket_Unknown = 0; //未知市场
    TrdSecMarket_HK = 1; //香港市场（股票、窝轮、牛熊、期权、期货等）
    TrdSecMarket_US = 2; //美国市场（股票、期权、期货等）
    TrdSecMarket_CN_SH = 31; //沪股市场（股票）
    TrdSecMarket_CN_SZ = 32; //深股市场（股票）
    TrdSecMarket_SG = 41;  //新加坡市场（期货）  
    TrdSecMarket_JP = 51;  //日本市场（期货）  
    TrdSecMarket_AU = 61; // 澳大利亚  
    TrdSecMarket_MY = 71; // 马来西亚  
    TrdSecMarket_CA = 81; // 加拿大  
    TrdSecMarket_FX = 91; // 外汇  
}
```

## 交易方向

**TrdSide**

```protobuf
enum TrdSide
{
    //客户端下单只传 Buy 或 Sell 即可，SellShort 是美股订单时服务器返回有此方向，BuyBack 目前不存在，但也不排除服务器会传
    TrdSide_Unknown = 0; //未知方向
    TrdSide_Buy = 1; //买入
    TrdSide_Sell = 2; //卖出
    TrdSide_SellShort = 3; //卖空
    TrdSide_BuyBack = 4; //买回
}
```

:::tip 提示
**下单** 接口的交易方向 ，建议仅使用 `买入` 和 `卖出` 两个方向作为入参。  
`卖空` 和 `买回` 仅适用于日本券商，其他券商仅用于 **查询今日订单** ，**查询历史订单** ，**响应订单推送回调** ，**查询当日成交** ，**查询历史成交** ，**响应成交推送回调** 接口的返回字段展示。
:::

## 订单有效期

**TimeInForce**

```protobuf
enum TimeInForce
{
    TimeInForce_DAY = 0;       // 当日有效
    TimeInForce_GTC = 1;       // 撤单前有效，最多持续90自然日。
    TimeInForce_IOC = 2;       // 立即成交或取消（仅适用于加密货币市价单）
    TimeInForce_GTD = 3;       // 指定日期前有效
}
```

## 账户所属券商

**SecurityFirm**

```protobuf
enum SecurityFirm
{
    SecurityFirm_Unknown = 0;        //未知
    SecurityFirm_FutuSecurities = 1; //富途证券（香港）
    SecurityFirm_FutuInc = 2;        //moomoo证券(美国)
    SecurityFirm_FutuSG = 3;        //moomoo证券(新加坡)
    SecurityFirm_FutuAU = 4;         //moomoo证券(澳大利亚)
    SecurityFirm_FutuCA = 5;         //富途证券（加拿大）
    SecurityFirm_FutuMY = 6;         //富途证券（马来西亚）
    SecurityFirm_FutuJP = 7;         //富途证券（日本）
}
```

## 模拟交易账户类型

**SimAccType**

```protobuf
enum SimAccType
{
    SimAccType_Unknown = 0;		//未知
    SimAccType_Stock = 1;		//股票模拟账户（仅用于交易证券类产品，不支持交易期权）
    SimAccType_Option = 2;      //期权模拟账户（仅用于交易期权，不支持交易股票证券类产品）
    SimAccType_Futures = 3;      //期货模拟账户
    SimAccType_StockAndOption = 4;      //美股融资融券模拟账户
}
```

## 风险状态

**CltRiskStatus**

```protobuf
enum CltRiskStatus
{
  CltRiskStatus_Level1 = 0;  //非常安全
  CltRiskStatus_Level2 = 1;  //安全
  CltRiskStatus_Level3 = 2;  //较安全
  CltRiskStatus_Level4 = 3;  //较低风险
  CltRiskStatus_Level5 = 4;  //中等风险
  CltRiskStatus_Level6 = 5;  //较高风险
  CltRiskStatus_Level7 = 6;  //预警
  CltRiskStatus_Level8 = 7;  //预警
  CltRiskStatus_Level9 = 8;  //预警
}
```

## 持仓限额状态

**ExposureLevel**

```protobuf
enum ExposureLevel
{
    ExposureLevel_Unknown = 0;    //未知
    ExposureLevel_Normal = 1;     //正常
    ExposureLevel_NearLimit = 2;  //即将用尽
    ExposureLevel_Restricted = 3; //受限
    ExposureLevel_Safe = 4;       //安全
    ExposureLevel_Moderate = 5;   //适中
    ExposureLevel_Warning = 6;    //预警
    ExposureLevel_MarginCall = 7; //危险
}
```

## 日内交易限制情况

**DTStatus**

```protobuf
enum DTStatus
{
	DTStatus_Unknown = 0; 		//未知
	DTStatus_Unlimited = 1;		//无限次(当前可以无限次日内交易，注意留意剩余日内交易购买力)
	DTStatus_EMCall = 2;		//EM Call(当前状态不能新建仓位，需要补充资产净值至$25000以上，否则会被禁止新建仓位90天)
	DTStatus_DTCall = 3;		//DT Call(当前状态有未补平的日内交易追缴金额（DTCall），需要在5个交易日内足额入金来补平 DTCall，否则会被禁止新建仓位，直到足额存入资金才会解禁)
}
```

## 现金流方向

**TrdCashFlowDirection**

```protobuf
enum TrdCashFlowDirection
{
	TrdCashFlowDirection_Unknown = 0; //未知
	TrdCashFlowDirection_In = 1; //现金流入
	TrdCashFlowDirection_Out = 2; //现金流出
}
```

## 日本子账户类型

**TrdSubAccType**

```protobuf
enum TrdSubAccType
{
	TrdSubAccType_None = 0; //未知
	TrdSubAccType_JP_GENERAL = 1; // 一般-Long
	TrdSubAccType_JP_TOKUTEI = 2; // 特定-Long
	TrdSubAccType_JP_NISA_GENERAL = 3; // 一般NISA
	TrdSubAccType_JP_NISA_TSUMITATE = 4; // 累计NISA

	TrdSubAccType_JP_GENERAL_SHORT = 5; // 一般-short
	TrdSubAccType_JP_TOKUTEI_SHORT = 6; // 特定-short
	TrdSubAccType_JP_HONPO_GENERAL = 7; // 本国信用交易抵押品-一般
	TrdSubAccType_JP_GAIKOKU_GENERAL = 8; // 外国信用交易抵押品-一般
	TrdSubAccType_JP_HONPO_TOKUTEI = 9; // 本国信用交易抵押品-特定
	TrdSubAccType_JP_GAIKOKU_TOKUTEI = 10; // 外国信用交易抵押品-特定

	TrdSubAccType_JP_DERIVATIVE_LONG = 11; // 衍生品子账户-Long
	TrdSubAccType_JP_DERIVATIVE_SHORT = 12; // 衍生品子账户-Short
	TrdSubAccType_JP_HONPO_DERIVATIVE_GENERAL = 13; // 本国衍生品证据金子账户-一般
	TrdSubAccType_JP_GAIKOKU_DERIVATIVE_GENERAL = 14; // 外国衍生品证据金子账户-一般
	TrdSubAccType_JP_HONPO_DERIVATIVE_TOKUTEI = 15; // 本国衍生品证据金子账户-特定
	TrdSubAccType_JP_GAIKOKU_DERIVATIVE_TOKUTEI = 16; // 外国衍生品证据金子账户-特定
}
```

## 资产类别

**TrdAssetCategory**

```protobuf
enum TrdAssetCategory
{
	TrdAssetCategory_Unknown = 0; 	//未知
	TrdAssetCategory_JP = 1;	    //本国
	TrdAssetCategory_US = 2;	    //外国
}
```

## 交易品类

**TrdCategory**

```protobuf
enum TrdCategory
{
    TrdCategory_Unknown = 0; //未知品类
    TrdCategory_Security = 1; //证券
    TrdCategory_Future = 2; //期货
    TrdCategory_Crypto = 3; //加密货币
}
```

## 账户现金信息

**AccCashInfo**

```protobuf
message AccCashInfo
{
    optional int32 currency = 1;        // 货币类型，取值参考 Currency
    optional double cash = 2;           // 现金结余
    optional double availableBalance = 3;   // 现金可提金额
    optional double netCashPower = 4;		// 现金购买力
}
```

## 分市场资产信息

**AccMarketInfo**

```protobuf
message AccCashInfo
{
    optional int32 trdMarket = 1;        // 交易市场, 参见TrdMarket的枚举定义
    optional double assets = 2;          // 分市场资产信息
}
```


## 交易协议公共参数头

**TrdHeader**

```protobuf
message TrdHeader
{
  required int32 trdEnv = 1; //交易环境, 参见 TrdEnv 的枚举定义
  required uint64 accID = 2; //业务账号, 业务账号与交易环境、市场权限需要匹配，否则会返回错误
  required int32 trdMarket = 3; //交易市场, 参见 TrdMarket 的枚举定义
  optional int32 jpAccType = 4; //JP子账户类型，取值见 TrdSubAccType
}
```

## 交易业务账户

**TrdAcc**

```protobuf
message TrdAcc
{
  required int32 trdEnv = 1; //交易环境，参见 TrdEnv 的枚举定义
  required uint64 accID = 2; //业务账号
  repeated int32 trdMarketAuthList = 3; //业务账户支持的交易市场权限，即此账户能交易那些市场, 可拥有多个交易市场权限，目前仅单个，取值参见 TrdMarket 的枚举定义
  optional int32 accType = 4;   //账户类型，取值见 TrdAccType
  optional string cardNum = 5;  //卡号
  optional int32 securityFirm = 6; //所属券商，取值见SecurityFirm
  optional int32 simAccType = 7; //模拟交易账号类型，取值见SimAccType
  optional string uniCardNum = 8;  //所属综合账户卡号
  optional int32 accStatus = 9; //账号状态，取值见TrdAccStatus
  optional int32 accRole = 10; //账号分类，是不是主账号，取值见TrdAccRole
  repeated int32 jpAccType = 11; //JP子账户类型，取值见 TrdSubAccType
}
```


## 账户资金

**Funds**

```protobuf
message Funds
{
  required double power = 1; //最大购买力（此字段是按照 50% 的融资初始保证金率计算得到的 近似值。但事实上，每个标的的融资初始保证金率并不相同。我们建议您使用 查询最大可买可卖 接口返回的 最大可买 字段，来判断实际可买入的最大数量）
  required double totalAssets = 2; //资产净值
  required double cash = 3; //现金（仅单币种账户使用此字段，综合账户请使用 cashInfoList 获取分币种现金）
  required double marketVal = 4; //证券市值, 仅证券账户适用
  required double frozenCash = 5; //冻结资金
  required double debtCash = 6; //计息金额
  required double avlWithdrawalCash = 7; //现金可提（仅单币种账户使用此字段，综合账户请使用 cashInfoList 获取分币种现金可提）

  optional int32 currency = 8;            //币种，本结构体资金相关的货币类型，取值参见 Currency，期货和综合证券账户适用
  optional double availableFunds = 9;     //可用资金，期货适用
  optional double unrealizedPL = 10;      //未实现盈亏，期货适用
  optional double realizedPL = 11;        //已实现盈亏，期货适用
  optional int32 riskLevel = 12;           //风控状态，参见 CltRiskLevel, 期货适用。建议统一使用 riskStatus 字段获取证券、期货账户的风险状态
  optional double initialMargin = 13;      //初始保证金
  optional double maintenanceMargin = 14;  //维持保证金
  repeated AccCashInfo cashInfoList = 15;  //分币种的现金、现金可提和现金购买力（仅综合账户适用）
  optional double maxPowerShort = 16; //卖空购买力（此字段是按照 60% 的融券保证金率计算得到的近似值。但事实上，每个标的的融券保证金率并不相同。我们建议您使用 查询最大可买可卖 接口返回的 可卖空 字段，来判断实际可卖空的最大数量。）
  optional double netCashPower = 17;  //现金购买力（仅单币种账户使用此字段，综合账户请使用 cashInfoList 获取分币种现金购买力）
  optional double longMv = 18;        //多头市值
  optional double shortMv = 19;       //空头市值
  optional double pendingAsset = 20;  //在途资产
  optional double maxWithdrawal = 21;          //融资可提，仅证券账户适用
  optional int32 riskStatus = 22;              //风险状态，参见 CltRiskStatus，共分 9 个等级，LEVEL1是最安全，LEVEL9是最危险
  optional double marginCallMargin = 23;       //	Margin Call 保证金

  optional bool isPdt = 24;				//是否PDT账户，仅moomoo证券(美国)账户适用
  optional string pdtSeq = 25;			//剩余日内交易次数，仅被标记为 PDT 的moomoo证券(美国)账户适用
  optional double beginningDTBP = 26;		//初始日内交易购买力，仅被标记为 PDT 的moomoo证券(美国)账户适用
  optional double remainingDTBP = 27;		//剩余日内交易购买力，仅被标记为 PDT 的moomoo证券(美国)账户适用
  optional double dtCallAmount = 28;		//日内交易待缴金额，仅被标记为 PDT 的moomoo证券(美国)账户适用
  optional int32 dtStatus = 29;				//日内交易限制情况，取值见 DTStatus。仅被标记为 PDT 的moomoo证券(美国)账户适用
  
  optional double securitiesAssets = 30; // 证券资产净值
  optional double fundAssets = 31; // 基金资产净值
  optional double bondAssets = 32; // 债券资产净值

  repeated AccMarketInfo marketInfoList = 33; //分市场资产信息

  optional double cryptoMv = 34; // 加密货币市值
  optional int32 exposureLevel = 35; // 持仓限额状态，取值见 ExposureLevel
  optional double exposureLimit = 36; // 持仓限额
  optional double usedLimit = 37; // 已用持仓限额
  optional double remainingLimit = 38; // 剩余持仓限额
}
```

## 账户持仓

**Position**

```protobuf
message Position
{
    required uint64 positionID = 1;     //持仓 ID，一条持仓的唯一标识
    required int32 positionSide = 2;    //持仓方向，参见 PositionSide 的枚举定义
    required string code = 3;           //代码
    required string name = 4;           //名称
    required double qty = 5;            //持有数量，2位精度，期权单位是"张"，下同
    required double canSellQty = 6;     //可用数量，是指持有的可平仓的数量。可用数量=持有数量-冻结数量。期权和期货的单位是“张”。
    required double price = 7;          //市价，3位精度，期货为2位精度
    optional double costPrice = 8;      //摊薄成本价（证券账户），平均开仓价（期货账户）。证券无精度限制，期货为2位精度，如果没传，代表此时此值无效
    required double val = 9;            //市值，3位精度, 期货此字段值为0
    required double plVal = 10;         //盈亏金额，3位精度，期货为2位精度
    optional double plRatio = 11;       //盈亏百分比(平均成本价模式)，无精度限制，如果没传，代表此时此值无效
    optional int32 secMarket = 12;      //证券所属市场，参见 TrdSecMarket 的枚举定义
    
	//以下是此持仓今日统计
    optional double td_plVal = 21;      //今日盈亏金额，3位精度，下同, 期货为2位精度
    optional double td_trdVal = 22;     //今日交易额，期货不适用
    optional double td_buyVal = 23;     //今日买入总额，期货不适用
    optional double td_buyQty = 24;     //今日买入总量，期货不适用
    optional double td_sellVal = 25;    //今日卖出总额，期货不适用
    optional double td_sellQty = 26;    //今日卖出总量，期货不适用

    optional double unrealizedPL = 28;       //未实现盈亏（仅期货账户适用）
    optional double realizedPL = 29;         //已实现盈亏（仅期货账户适用）	
    optional int32 currency = 30;        // 货币类型，取值参考 Currency
    optional int32 trdMarket = 31;  //交易市场, 参见 TrdMarket 的枚举定义

    optional double dilutedCostPrice = 32;      //摊薄成本价，仅支持证券账户使用
    optional double averageCostPrice = 33;      //平均成本价，模拟交易证券账户不适用
    optional double averagePlRatio = 34;        //盈亏百分比(平均成本价模式)，无精度限制，如果没传，代表此时此值无效

    optional uint64 comboID = 35;       //期权策略组合 ID
    optional int32 strategyType = 36;   //期权策略类型，参见 Qot_Common.OptionStrategyType 的枚举定义
    optional int32 positionType = 37;   //期权组合持仓类型，参见 PositionType 的枚举定义
    optional uint64 accID = 38;         //交易业务账户 ID
    optional int32 jpAccType = 39;      //日本子账户类型，取值见 TrdSubAccType
}
```

## 订单

**Order**

```protobuf
message Order
{
    required int32 trdSide = 1; //交易方向, 参见 TrdSide 的枚举定义
    required int32 orderType = 2; //订单类型, 参见 OrderType 的枚举定义
    required int32 orderStatus = 3; //订单状态, 参见 OrderStatus 的枚举定义
    required uint64 orderID = 4; //订单号
    required string orderIDEx = 5; //扩展订单号(仅查问题时备用)
    required string code = 6; //代码
    required string name = 7; //名称
    required double qty = 8; //订单数量，2位精度，期权单位是"张"
    optional double price = 9; //订单价格，3位精度
    required string createTime = 10; //创建时间，严格按 YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD HH:MM:SS.MS 格式传
    required string updateTime = 11; //最后更新时间，严格按 YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD HH:MM:SS.MS 格式传
    optional double fillQty = 12; //成交数量，2位精度，期权单位是"张"
    optional double fillAvgPrice = 13; //成交均价，无精度限制
    optional string lastErrMsg = 14; //最后的错误描述，如果有错误，会有此描述最后一次错误的原因，无错误为空
    optional int32 secMarket = 15; //证券所属市场，参见 TrdSecMarket 的枚举定义
    optional double createTimestamp = 16; //创建时间戳
    optional double updateTimestamp = 17; //最后更新时间戳
    optional string remark = 18; //用户备注字符串，最大长度64字节
    optional double auxPrice = 21; //触发价格
    optional int32 trailType = 22; //跟踪类型, 参见Trd_Common.TrailType的枚举定义
    optional double trailValue = 23; //跟踪金额/百分比
    optional double trailSpread = 24; //指定价差
    optional int32 currency = 25;        // 货币类型，取值参考 Currency
    optional int32 trdMarket = 26;  //交易市场, 参见TrdMarket的枚举定义
    optional int32 session = 27; //美股订单时段, 参见Common.Session的枚举定义
    optional int32 jpAccType = 28; //JP子账户类型，取值见 TrdSubAccType
    optional string expireTime = 29;  //timeInForce为GTD时，表示订单到期时间
    optional double orderAmount = 30;  // 订单金额
    optional int32 strategyType = 31;  // 期权策略类型，参见Qot_Common.OptionStrategyType的枚举定义
    repeated Qot_Common.ComboLeg comboLegs = 32; //组合期权各腿数据
}
```

## 订单费用条目

**OrderFeeItem**

```protobuf
message OrderFeeItem
{
    optional string title = 1; //费用名字
    optional double value = 2; //费用金额
}
```

## 订单费用

**OrderFee**

```protobuf
message OrderFee
{
    required string orderIDEx = 1; //扩展订单号
    optional double feeAmount = 2; //费用总额
    repeated OrderFeeItem feeList = 3; //费用明细
}
```

## 成交

**OrderFill**

```protobuf
message OrderFill
{
	required int32 trdSide = 1; //交易方向, 参见 TrdSide 的枚举定义
    required uint64 fillID = 2; //成交号
    required string fillIDEx = 3; //扩展成交号(仅查问题时备用)
    optional uint64 orderID = 4; //订单号
    optional string orderIDEx = 5; //扩展订单号(仅查问题时备用)
    required string code = 6; //代码
    required string name = 7; //名称
    required double qty = 8; //成交数量，2位精度，期权单位是"张"
    required double price = 9; //成交价格，3位精度
    required string createTime = 10; //创建时间（成交时间），严格按 YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD HH:MM:SS.MS 格式传
    optional int32 counterBrokerID = 11; //对手经纪号，港股有效
    optional string counterBrokerName = 12; //对手经纪名称，港股有效
    optional int32 secMarket = 13; //证券所属市场，参见 TrdSecMarket 的枚举定义
    optional double createTimestamp = 14; //创建时间戳
    optional double updateTimestamp = 15; //最后更新时间戳
    optional int32 status = 16; //成交状态, 参见 OrderFillStatus 的枚举定义
    optional int32 trdMarket = 17;  //交易市场, 参见TrdMarket的枚举定义
    optional int32 jpAccType = 18; //JP子账户类型，取值见 TrdSubAccType
}
```

## 最大可交易数量

**MaxTrdQtys**

```protobuf
message MaxTrdQtys
{
	//因目前服务器实现的问题，卖空需要先卖掉多头持仓才能再卖空，是分开两步卖的，买回来同样是逆向两步；而看多的买是可以现金加融资一起一步买的，请注意这个差异
	required double maxCashBuy = 1;             //现金可买（期权的单位是“张”，期货账户不适用）
    optional double maxCashAndMarginBuy = 2;    //最大可买（期权的单位是“张”，期货账户不适用）
    required double maxPositionSell = 3;        //持仓可卖（期权的单位是“张”）
    optional double maxSellShort = 4;           //可卖空（期权的单位是“张”，期货账户不适用）
    optional double maxBuyBack = 5;             //平仓需买入（当持有净空仓时，必须先买回空头持仓的股数，才能再继续买多。期货、期权的单位是“张”）
    optional double longRequiredIM = 6;         //买 1 张合约所带来的初始保证金变动。仅期货和期权适用。无持仓时，返回 买入 1 张的初始保证金占用（正数）。有多仓时，返回 买入1 张的初始保证金占用（正数）。有空仓时，返回 买回 1 张的初始保证金释放（负数）。
    optional double shortRequiredIM = 7;        //卖 1 张合约所带来的初始保证金变动。仅期货和期权适用。无持仓时，返回 卖空 1 张的初始保证金占用（正数）。 有多仓时，返回卖出1 张的初始保证金占用（正数）。有空仓时，返回 卖空1 张的初始保证金释放（正数）。
}
```

## 组合可交易信息

**ComboMaxTrdQtys**

```protobuf
message ComboMaxTrdQtys
{
    optional double nlvChange = 1;    //综合净资产变动
    optional double initialMarginChange = 2;    //初始保证金变动
    optional double maintenanceMarginChange = 3;    //维持保证金变动
    optional double optionBuyPower = 4;    //期权购买力
    optional double maxWithDrawChange = 5;    //最大可提变动
    optional double buyPowerDecrease = 6;    //消耗购买力
}
```

## 组合腿

**ComboLeg**

```protobuf
message ComboLeg
{
	required Qot_Common.Security security = 1; //股票/期权
    optional int32 side = 2; //方向，取值见 Trd_Common.TrdSide
    optional double qtyRatio = 3; //数量比例
    optional uint64 positionID = 4; //持仓ID，仅 moomoo JP 平仓时使用
}
```

## 现金流水数据

**FlowSummaryInfo**

```protobuf
message FlowSummaryInfo
{
	optional string clearingDate = 1; //清算日期
	optional string settlementDate = 2; //结算日期
	optional int32 currency = 3; //币种
	optional string cashFlowType = 4; //现金流类型
	optional int32 cashFlowDirection = 5; //现金流方向 TrdCashFlowDirection
	optional double cashFlowAmount = 6; //金额
	optional string cashFlowRemark = 7; //备注
	optional uint64 cashFlowID = 8; //现金流 ID
}
```

## 过滤条件

**TrdFilterConditions**

```protobuf
message TrdFilterConditions
{
  repeated string codeList = 1; //代码过滤，只返回包含这些代码的数据，没传不过滤
  repeated uint64 idList = 2; //ID 主键过滤，只返回包含这些 ID 的数据，没传不过滤，订单是 orderID、成交是 fillID、持仓是 positionID
  optional string beginTime = 3; //开始时间，严格按 YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD HH:MM:SS.MS 格式传，对持仓无效，拉历史数据必须填
  optional string endTime = 4; //结束时间，严格按 YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD HH:MM:SS.MS 格式传，对持仓无效，拉历史数据必须填
  repeated string orderIDExList = 5; // 服务器订单ID列表，可以用来替代orderID列表，二选一
  optional int32 filterMarket = 6; //指定交易市场, 参见TrdMarket的枚举定义
}
```

---

# 基础功能


## 设置接口信息


## 设置协议格式


## 对所有连接设置协议加密

`start(ip, port, ssl, key)`


* **介绍**

    初始化连接，连接并初始化

* **参数**
    - ip: OpenD 监听的 WebSocket 地址
    - port: OpenD 监听的 WebSocket 端口
    - ssl: 是否启用 SSL 加密，参见 [WebSocket 相关](../qa/other.html#6319)
    - key：连接的密钥，否则会连接超时，密钥在在 OpenD 可配置，UI 版本在不指定的情况下会随机指定

* **Example**

```js
import ftWebSocket from "@/components/ft-websocket/main.js";
class Example {
    example() {
        this.websocket = new ftWebSocket();
        this.websocket.start("127.0.0.1", 33333, true, '123456');
    }
}
```


## 设置私钥路径

`start(ip, port, ssl, key)`

* **介绍**

    初始化连接，连接并初始化

* **参数**
    - ip: OpenD 监听的 WebSocket 地址
    - port: OpenD 监听的 WebSocket 端口
    - ssl: 是否启用 SSL 加密，参见 [WebSocket 相关](../qa/other.html#6319)
    - key：连接的密钥，否则会连接超时，密钥在在 OpenD 可配置，UI 版本在不指定的情况下会随机指定
    

* **Example**

```js
import ftWebSocket from "@/components/ft-websocket/main.js";
class Example {
    example() {
        this.websocket = new ftWebSocket();
        this.websocket.start("127.0.0.1", 33333, true, '123456');
    }
}
```

## 设置线程模式


## 设置回调

`onPush(cmd, res)`  
`onlogin(ret, msg)`

* **介绍**

    登录回调以及推送回调

* **返回**
    - cmd: 推送协议 ID
    - res: 推送协议内容
    - ret: 是否成功初始化
    - msg: 失败描述

* **Example**

```js
import ftWebSocket from "@/components/ft-websocket/main.js";
class Example {
    example() {
        this.websocket = new ftWebSocket();
        this.websocket.start("127.0.0.1", 33333, false, null);
        this.websocket.onPush = this.onPush.bind(this);
        this.websocket.onlogin = this.onLogin.bind(this);
    },
    onPush(cmd, res) {
    const obj = ftWebSocket.findCmdObj(cmd);
        if (obj && obj.description) {
            console.log(res);
        }
    },
    onLogin(ret, msg) {
        if (ret) {
            console.log(this.websocket.getConnID());
        }
    }
}
```

## 获取连接 ID

`getConnID()`

* **介绍**

    获取连接 ID，连接初始化成功后才会有值

* **返回**
    - connID: 连接 ID

* **Example**

```js
import ftWebSocket from "@/components/ft-websocket/main.js";
class Example {
    example() {
        this.websocket = new ftWebSocket();
        this.websocket.start("127.0.0.1", 33333, false, null);
        this.websocket.onlogin = this.onLogin.bind(this);
    },
    onLogin(ret, msg) {
    if (ret) {
        this.websocket.getConnID();
    }
}
```

## 事件通知回调

`onPush(cmd, res)`

* **介绍**

    通知 OpenD 一些重要消息，类似连接断开等

* **Example**
```js
import ftWebSocket from "@/components/ft-websocket/main.js";
class Example {
    example() {
        this.websocket = new ftWebSocket();
        this.websocket.start("127.0.0.1", 33333, false, null);
        this.websocket.onPush = this.onPush.bind(this);
        this.websocket.onlogin = this.onLogin.bind(this);
    },
    onPush(cmd, res) {
    const obj = ftWebSocket.findCmdObj(cmd);
        if (obj && obj.description && cmd == 1003) {
            console.log(res);
        }
    },
    onLogin(ret, msg) {
        if (ret) {
            console.log(this.websocket.getConnID());
        }
    }
}
```

## 设置是否在控制台打印连接信息

---

# 通用定义

## 接口调用结果

**RetType**  

```protobuf
enum RetType
{
    RetType_Succeed = 0; //成功
    RetType_Failed = -1; //失败
    RetType_TimeOut = -100; //超时
    RetType_Unknown = -400; //未知结果
}
```

## 协议格式

**ProtoFmt**  

```protobuf
enum ProtoFmt
{
    ProtoFmt_Protobuf = 0; //Google Protobuf 格式
    ProtoFmt_Json = 1; //Json 格式
}
```

## 包加密算法

**PacketEncAlgo**  

```protobuf
enum PacketEncAlgo
{
    PacketEncAlgo_FTAES_ECB = 0; //修改过的 AES 的 ECB 加密模式
    PacketEncAlgo_None = -1; //不加密
    PacketEncAlgo_AES_ECB = 1; //标准的 AES 的 ECB 加密模式
    PacketEncAlgo_AES_CBC = 2; //标准的 AES 的 CBC 加密模式
}
```

## 程序状态类型

**ProgramStatusType**  

```protobuf
enum ProgramStatusType
{
    ProgramStatusType_None = 0;
    ProgramStatusType_Loaded = 1; //已完成类似加载配置,启动服务器等操作,服务器启动之前的状态无需返回

    ProgramStatusType_Loging = 2; //登录中
    ProgramStatusType_NeedPicVerifyCode = 3; //需要图形验证码
    ProgramStatusType_NeedPhoneVerifyCode = 4; //需要手机验证码
    ProgramStatusType_LoginFailed = 5; //登录失败,详细原因在描述返回
    ProgramStatusType_ForceUpdate = 6; //客户端版本过低

    ProgramStatusType_NessaryDataPreparing = 7; //正在拉取类似免责声明等一些必要信息
    ProgramStatusType_NessaryDataMissing = 8; //缺少必要信息
    ProgramStatusType_UnAgreeDisclaimer = 9; //未同意免责声明
    ProgramStatusType_Ready = 10; //可以接收业务协议收发,正常可用状态
	
    //OpenD 登录后被强制退出登录，会导致连接全部断开,需要重连后才能得到以下该状态（并且需要在 ui 模式下）
    ProgramStatusType_ForceLogout = 11; //被强制退出登录,例如修改了登录密码,中途打开设备锁等,详细原因在描述返回

    ProgramStatusType_DisclaimerPullFailed = 12; //拉取免责声明标志失败
}
```

## 网关事件通知类型

**GtwEventType**  

```protobuf
enum GtwEventType
{
    GtwEventType_None = 0; //正常无错
    GtwEventType_LocalCfgLoadFailed	= 1; //加载本地配置失败
    GtwEventType_APISvrRunFailed = 2; //服务器启动失败
	  GtwEventType_ForceUpdate = 3; //客户端版本过低
	  GtwEventType_LoginFailed = 4; //登录失败
	  GtwEventType_UnAgreeDisclaimer = 5; //未同意免责声明
	  GtwEventType_NetCfgMissing = 6; //缺少必要网络配置信息;例如控制订阅额度 //已优化，不会再出现该情况
	  GtwEventType_KickedOut = 7; //牛牛帐号在别处登录
	  GtwEventType_LoginPwdChanged = 8; //登录密码被修改
	  GtwEventType_BanLogin = 9; //用户被禁止登录
	  GtwEventType_NeedPicVerifyCode = 10; //需要图形验证码
	  GtwEventType_NeedPhoneVerifyCode = 11; //需要手机验证码
	  GtwEventType_AppDataNotExist = 12; //程序自带数据不存在
	  GtwEventType_NessaryDataMissing = 13; //缺少必要数据
	  GtwEventType_TradePwdChanged = 14; //交易密码被修改
	  GtwEventType_EnableDeviceLock = 15; //启用设备锁
}
```


## 系统通知类型

**NotifyType**  

```protobuf
enum NotifyType
{
    NotifyType_None = 0; //无
	  NotifyType_GtwEvent = 1; //OpenD 运行事件通知
	  NotifyType_ProgramStatus = 2; //程序状态
	  NotifyType_ConnStatus = 3; //连接状态
	  NotifyType_QotRight = 4; //行情权限
	  NotifyType_APILevel = 5; //用户等级，已在2.10版本之后废弃
	  NotifyType_APIQuota = 6; //API 额度
}
```

## 包唯一标识

**PacketID** 

```protobuf
message PacketID
{
	  required uint64 connID = 1; //当前 TCP 连接的连接 ID，一条连接的唯一标识，InitConnect 协议会返回
	  required uint32 serialNo = 2; //自增序列号
}
```

## 程序状态

**ProgramStatus**

```protobuf
message ProgramStatus
{
	  required ProgramStatusType type = 1; //当前状态
	  optional string strExtDesc = 2; // 额外描述
}
```

---

# 底层协议介绍

Futu API 是富途为主流的编程语言（Python、Java、C#、C++、JavaScript）封装的 API SDK，以方便您调用，降低策略开发难度。  
这部分主要介绍策略脚本与 OpenD 服务之间通信的底层协议，适用于非上述 5 种编程语言用户，自行对接实现底层裸协议。

:::tip 提示
* 如果您使用的编程语言在上述的 5 种主流编程语言之内，可以直接跳过这部分内容。
:::

## 协议请求流程
* 建立连接
* 初始化连接
* 请求数据或接收推送数据
* 定时发送 KeepAlive 保持连接

![proto-process](../img/proto-process.png)


## 协议设计
协议数据包括协议头以及协议体，协议头固定字段，协议体根据具体协议决定。

### 协议头

```
struct APIProtoHeader
{
    u8_t szHeaderFlag[2];
    u32_t nProtoID;
    u8_t nProtoFmtType;
    u8_t nProtoVer;
    u32_t nSerialNo;
    u32_t nBodyLen;
    u8_t arrBodySHA1[20];
    u8_t arrReserved[8];
};
```
字段|说明
:-|:-
szHeaderFlag|包头起始标志，固定为“FT”
nProtoID|协议 ID
nProtoFmtType|协议格式类型，0 为 Protobuf 格式，1 为 Json 格式
nProtoVer|协议版本，用于迭代兼容，目前填 0
nSerialNo|包序列号，用于对应请求包和回包，要求递增
nBodyLen|包体长度
arrBodySHA1|包体原始数据(解密后)的 SHA1 哈希值
arrReserved|保留 8 字节扩展

::: tip 提示
* u8_t 表示 8 位无符号整数，u32_t 表示 32 位无符号整数
* OpenD 内部处理使用 Protobuf，因此协议格式建议使用 Protobuf，减少 Json 转换开销
* nProtoFmtType 字段指定了包体的数据类型，回包会回对应类型的数据；推送协议数据类型由 OpenD 配置文件指定
* **arrBodySHA1 用于校验请求数据在网络传输前后的一致性，必须正确填入**
* **协议头的二进制流使用的是小端字节序，即一般不需要使用 ntohl 等相关函数转换数据**
:::

### 协议体
#### Protobuf 协议请求包体结构
```
message C2S
{
    required int64 req = 1;
}

message Request
{
    required C2S c2s = 1;
}
```

#### Protobuf 协议回应包体结构
```
message S2C
{
    required int64 data = 1;
}

message Response
{
    required int32 retType = 1 [default = -400]; //RetType，返回结果
    optional string retMsg = 2;
    optional int32 errCode = 3;
    optional S2C s2c = 4;
}
```

字段|说明
:-|:-
c2s|请求参数结构
req|请求参数，实际根据协议定义
retType|请求结果
retMsg|若请求失败，说明失败原因
errCode|若请求失败对应错误码
s2c|回应数据结构，部分协议不返回数据则无该字段
data|回应数据，实际根据协议定义

::: tip 提示
* 包体格式类型请求包由协议头 nProtoFmtType 指定，OpenD 主动推送格式在 [InitConnect](../ftapi/init.md#1515) 设置。
* 原始协议文件格式是以 Protobuf 格式定义，若需要 json 格式传输，建议使用 protobuf3 的接口直接转换成 json。
* 枚举值字段定义使用有符号整形，注释指明对应枚举，枚举一般定义于 Common.proto，Qot_Common.proto，Trd_Common.proto 文件中。
* 协议中价格、百分比等数据用浮点类型来传输，直接使用会有精度问题，需要根据精度（如协议中未指明，默认小数点后三位）做四舍五入之后再使用。
:::

## 心跳保活

```protobuf
syntax = "proto2";
package KeepAlive;
option java_package = "com.futu.openapi.pb";
option go_package = "github.com/futuopen/ftapi4go/pb/keepalive";

import "Common.proto";

message C2S
{
	required int64 time = 1; //客户端发包时的格林威治时间戳，单位秒
}

message S2C
{
	required int64 time = 1; //服务器回包时的格林威治时间戳，单位秒
}

message Request
{
	required C2S c2s = 1;
}

message Response
{
	required int32 retType = 1 [default = -400]; //RetType,返回结果
	optional string retMsg = 2;
	optional int32 errCode = 3;
	
	optional S2C s2c = 4;
}
```

* **介绍**

    心跳保活

* **协议 ID**

    1004

* **使用**

    根据[初始化链接](./init.md#1990)返回的心跳保活间隔时间，向 OpenD 发送保活协议

## 加密通信流程

* 若 OpenD 配置了加密，[InitConnect](../ftapi/init.md#1515) 初始化连接协议必须使用 [RSA](../qa/other.md#4601) 公钥加密，后续其他协议使用 InitConnect 返回的随机密钥进行 AES 加密通信。
* OpenD 的加密流程借鉴了 SSL 协议，但考虑到一般是本地部署服务和应用，简化了相关流程，OpenD 与接入 Client 共用了同一个 [RSA](../qa/other.md#4601) 私钥文件，请妥善保存和分发私钥文件。
* 可到这个 [网址](http://web.chacuo.net/netrsakeypair) 在线生成随机 [RSA](../qa/other.md#4601) 密钥对，密钥格式必须为 PCKS#1，密钥长度 512，1024 都可以，不要设置密码，将生成的私钥复制保存到文件中，然后将私钥文件路径配置到 [OpenD 配置](../opend/opend-cmd.md#8799) 约定的 **rsa_private_key** 配置项中。
*  **建议有实盘交易的用户配置加密，避免账户和交易信息泄露。**

![encrypt](../img/encrypt.png)


## RSA 加解密
* [OpenD 配置](../opend/opend-cmd.md#8799) 约定 **rsa_private_key** 为私钥文件路径
* OpenD 与接入客户端共用相同的私钥文件
* RSA 加解密仅用于 InitConnect 请求，用于安全获取其它请求协议的对称加密 Key
* OpenD 的 [RSA](../qa/other.md#4601) 密钥为 1024 位，填充方式 PKCS1，公钥加密，私钥解密，公钥可通过私钥生成
* Python API 参考实现：[RsaCrypt](https://github.com/FutunnOpen/py-futu-api/tree/master/futu/common/sys_config.py) 类的 encrypt / decrypt 接口

### 发送数据加密
* RSA 加密规则:若密钥位数是 key_size，单次加密串的最大长度为 (key_size)/8 - 11，目前位数 1024，一次加密长度可定为 100。
* 将明文数据分成一个或数个最长 100 字节的小段进行加密，拼接分段加密数据即为最终的 Body 加密数据。

### 接收数据解密
* RSA 解密同样遵循分段规则，对于 1024 位密钥，每小段待解密数据长度为 128 字节。
* 将密文数据分成一个或数个 128 字节长的小段进行解密，拼接分段解密数据即为最终的 Body 解密数据。

## AES 加解密
* 加密 key 由 InitConnect 协议返回
* 默认使用的是 AES 的 ecb 加密模式。
* Python API 参考实现: [ConnMng](https://github.com/FutunnOpen/py-futu-api/tree/master/futu/common/conn_mng.py) 类的 encrypt_conn_data / decrypt_conn_data 接口

### 发送数据加密

* AES 加密要求源数据长度必须是 16 的整数倍，故需补‘0’对齐后再加密，记录 mod_len 为源数据长度与 16 取模值。
* 因加密前有可能对源数据作修改，故需在加密后的数据尾再增加一个 16 字节的填充数据块，其最后一个字节赋值 mod_len，其余字节赋值‘0’，将加密数据和额外的填充数据块拼接作为最终要发送协议的 body 数据。

### 接收数据解密

* 协议 body 数据，先将最后一个字节取出，记为 mod_len，然后将 body 截掉尾部 16 字节填充数据块后再解密（与加密填充额外数据块逻辑对应）。
* mod_len 为 0 时，上述解密后的数据即为协议返回的 body 数据，否则需截掉尾部(16 - mod_len)长度的用于填充对齐的数据。

![aes](../img/aes.png)

---

# OpenD 相关


## Q1：OpenD 因未完成“问卷评估及协议确认”自动退出

A: 您需要进行相关问卷评估及协议确认，才可以使用 OpenD，请先 [前往完成](https://www.futunn.com/about/api-disclaimer?lang=zh-CN)。

## Q2：OpenD 因”程序自带数据不存在“退出

A: 一般因权限问题导致自带数据拷贝失败，可以尝试将程序目录下 <font color=Gray> __*Appdata.dat*__ </font> 解压后的文件拷贝到程序数据目录下。

* windows 程序数据目录:`%appdata%/com.futunn.FutuOpenD/F3CNN`
* 非 windows 程序数据目录:`~/.com.futunn.FutuOpenD/F3CNN`

## Q3：OpenD 服务启动失败

A: 请检查：
1. 是否有其他程序占用所配置的端口；
2. 是否已经有配置了相同端口的 OpenD 在运行。

## Q4：如何验证手机验证码？

A: 在 OpenD 界面上或远程到 Telnet 端口，输入命令`input_phone_verify_code -code=123456`。

::: tip 提示
* 123456 是收到的手机验证码
* -code=123456 前有空格
:::

## Q5：是否支持其他编程语言？

A: OpenD 有对外提供基于 socket 的协议，目前我们提供并维护 Python，C++，Java，C# 和 JavaScript 接口，[下载入口](https://www.futunn.com/download/OpenAPI)。

如果上述语言仍不能满足您的需求，您可以自行对接 Protobuf 协议。

## Q6：在同一设备多次验证设备锁 

A: 设备标识随机生成并存放于 

windows: %appdata%/com.futunn.FutuOpenD/F3CNN/Device.dat 文件中。
非windows: ~/.com.futunn.FutuOpenD/F3CNN/Device.dat

::: tip 提示
1. 如果文件被删除或损坏，OpenD 会重新生成新设备标识，然后验证设备锁。  
2. 另外镜像拷贝部署的用户需要注意，如果多台机器的 Device.dat 内容相同，也会导致这些机器多次验证设备锁。删除 Device.dat 文件即可解决。
:::

## Q7：OpenD 是否有提供 Docker 镜像？

A: 目前没有提供。

## Q8：一个账号可以登录多个 OpenD 吗？

A: 一个账号可以在多台机器上登录 OpenD 或者其他客户终端，最多允许 10 个 OpenD 终端同时登录。同时有“行情互踢”的限制，只能有一个 OpenD 获得最高权限行情。例如：两个终端登录同一个账号，只能有一个港股 LV2 行情，另一个是港股 BMP 行情。

## Q9：如何控制 OpenD 和其他客户端（桌面端和移动端）的行情权限？

A: 应交易所的规定，多个终端同时在线会有“行情互踢”的限制，只能有一个终端获得最高权限行情。OpenD 命令行版本的启动参数中，内置了 [auto_hold_quote_right](../opend/opend-cmd.md#8799) 参数，用于灵活配置行情权限。当该参数选项开启时，OpenD 在行情权限被抢后，会自动抢回。如果 10 秒内再次被抢，则其他终端获得最高行情权限（OpenD 不会再抢）。

## Q10：如何优先保证 OpenD 行情权限？

A: 
1. 将 OpenD 启动参数 [auto_hold_quote_right](../opend/opend-cmd.md#8799) 配置为 1；
2. 保证不要在移动端或桌面端富途牛牛上在 10 秒内连续两次抢最高权限（登录算一次，点击“重启行情”算第二次）。

![quote-right-kick](../img/quote-right-kick.png)

## Q11：如何优先保证移动端（或桌面端）的行情权限？

A: OpenD 启动参数 [auto_hold_quote_right](../opend/opend-cmd.md#8799) 设置为 0，移动端或桌面端富途牛牛在 OpenD 之后登录即可。 

## Q12：使用可视化 OpenD 记住密码登录，长时间挂机后提示连接断开，需要重新登录？

A: 使用可视化 OpenD，如果选择记住密码登录，用的是记录在本地的令牌。由于令牌有时间限制，当令牌过期后，如果出现网络波动或富途后台发布，就可能导致与后台断开连接后无法自动连接上的情况。因此，可视化 OpenD 如果希望长时间挂机，建议手动输入密码登录，由 OpenD 自动处理该情况。


## Q13：遇到产品缺陷，如何请富途的研发工程师排查日志？

A: 
1. 与客服沟通问题表现，详述：发生错误的时间、OpenD 版本号、 API 版本号、脚本语言名、接口名或协议号、含详细入参和返回的短代码或截图。

2. 客服确认是产品缺陷后，如需进一步日志排查，研发工程师会主动联系。

3. 部分问题须提供 OpenD 日志，方便定位确认问题。交易类问题需要 info 日志级别，行情类问题需要 debug 日志级别。日志级别 log_level 可以在 <font color=Gray> __*OpenD.xml*__ </font> 中 [配置](../opend/opend-cmd.md#8799) ，配置后需要重启 OpenD 方能生效，待问题复现后，将该段日志打包发给富途研发工程师。

:::tip 提示
日志路径如下：  
windows：`%appdata%/com.futunn.FutuOpenD/Log`

非 windows：`~/.com.futunn.FutuOpenD/Log`
:::

## Q14：脚本连接不上 OpenD

A: 请先尝试检查：
1. 脚本连接的端口与 OpenD 配置的端口是否一致。
2. 由于 OpenD 连接上限为 128，是否有无用连接未关闭。
3. 检查监听地址是否正确，如果脚本和 OpenD 不在同一机器，OpenD 监听地址需要设置成 0.0.0.0 。

## Q15：连接上一段时间后断开

A: 如果是自己对接协议，检查下是否有定时发送心跳维持连接。


## Q16：Linux 下通过 multiprocessing 模块以多进程方式运行 Python 脚本，连不上 OpenD？

A: Linux/Mac 环境下以默认方式创建进程后，父进程中 py-futu-api 内部创建的线程将会在子进程中消失，导致程序内部状态错误。  
可以用 spawn 方式来启动进程：

```python
import multiprocessing as mp
mp.set_start_method('spawn')
p = mp.Process(target=func)
```


## Q17：如何在一台电脑同时登录两个 OpenD?

A: 可视化 OpenD 不支持，命令行 OpenD 支持。

1. 解压从官网下载的文件，复制整个命令行 OpenD 文件夹（如 OpenD_5.2.1408_Windows）得到副本（此处以 Windows 为例，其他系统可采取相同操作）。

![file-page](../img/nnfile-page.png)

2. 分别打开两个命令行 OpenD 文件夹配置好两份 OpenD.xml 文件。

第一份配置文件参数：api_port = 11111，login_account = 登录账号1，login_pwd = 登录密码1

第二份配置文件参数：api_port = 11112，login_account = 登录账号2，login_pwd = 登录密码2

![order-page](../img/nnorder-page.png)

3. 配置完成后，分别打开两个 OpenD 程序运行。

![fod-page](../img/nnfod-page.png)

4. 调用接口时，注意接口的参数`port`（OpenD 监听端口）与 OpenD.xml 文件中的参数`api_port`为对应关系  
例如：

```python
from futu import *

# 向账号1登录的 OpenD 进行请求
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111, is_encrypt=False)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽

# 向账号2登录的 OpenD 进行请求
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11112, is_encrypt=False)
quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
```

## Q18：行情权限被其他客户端踢掉，如何通过脚本执行抢权限的运维命令？
A：
1. 在OpenD启动参数中，配置好 Telnet 地址和 Telnet 端口。
![telnet_GUI](../img/telnet_GUI.jpg)
![telnet_CMD](../img/telnet_CMD.jpg)
2. 启动 OpenD（会同时启动 Telnet）。
3. 当发现行情权限被抢之后，您可以参考如下代码示例，通过 Telnet，向 OpenD 发送 `request_highest_quote_right` 命令。
```python
from telnetlib import Telnet
with Telnet('127.0.0.1', 22222) as tn:  # Telnet 地址为：127.0.0.1，Telnet 端口为：22222
    tn.write(b'request_highest_quote_right\r\n')
    reply = b''
    while True:
        msg = tn.read_until(b'\r\n', timeout=0.5)
        reply += msg
        if msg == b'':
            break
    print(reply.decode('gb2312'))
```

<span id="update-failed-qa"></span>

## Q19：OpenD 自动升级失败

A：
通过`update`命令执行 OpenD 自动更新失败，可能的原因：
- 文件被其他进程占用：可以尝试关闭其他 OpenD 进程，或者重启系统后，再次执行 `update`
如果以上仍无法解决，可以通过[官网](https://www.futunn.com/download/OpenAPI?lang=zh-CN)自行下载更新。

## Q20：ubuntu22无法启动可视化 OpenD？
A：
在有些Linux发行版（例如Ubuntu 22.04）运行可视化OpenD时，可能会提示：`dlopen(): error loading libfuse.so.2`。
这是因为这些系统没有默认安装libfuse。通常可以手动安装来解决，例如对于Ubuntu22.04，可以在命令行运行：
```
sudo apt update
sudo apt install -y libfuse2
```
安装成功后就可以正常运行可视化OpenD了。详细信息请参考：[https://docs.appimage.org/user-guide/troubleshooting/fuse.html](https://docs.appimage.org/user-guide/troubleshooting/fuse.html)。

## Q21：Linux上如何在后台运行命令行OpenD？


A：先切到 FutuOpenD 所在目录，配置好 FutuOpenD.xml 之后，执行如下命令
```
nohup ./FutuOpenD &
```

---

# 行情相关


## Q1：订阅失败

A: 订阅接口返回错误，有以下两类常见情况：
* 订阅额度不足：

  订阅额度规则参见 [订阅额度 & 历史 K 线额度](../intro/authority.md#1314)

* 订阅权限不足：

  支持订阅的行情权限见下表
  <table>
    <tr>
      <th> 市场 </th>
      <th> 品种 </th>
      <th> 支持订阅的行情权限 </th>
    </tr>
    <tr>
      <td rowspan="3"> 香港市场 </td>
      <td > 股票 </td>
      <td > LV1, LV2, SF </td>
    </tr>
    <tr>
	    <td> 期权</td>
      <td> LV1, LV2</td>
    </tr>
    <tr>
	    <td> 期货</td>
      <td> LV1, LV2</td>
    </tr>
    <tr>
      <td rowspan="3"> 美国市场 </td>
      <td > 股票 </td>
      <td > LV1, LV2 </td>
    </tr>
    <tr>
	    <td> 期权</td>
      <td> LV1</td>
    </tr>
    <tr>
	    <td> 期货</td>
      <td> LV1, LV2</td>
    </tr>
    <tr>
      <td > A 股市场 </td>
      <td > 股票 </td>
      <td > LV1 </td>
    </tr>
    <tr>
      <td > 新加坡市场 </td>
      <td > 股票 </td>
      <td > LV1, LV2 </td>
    </tr>
    <tr>
      <td > 马来西亚市场 </td>
      <td > 股票 </td>
      <td > LV1, LV2, LV3 </td>
    </tr>
    <tr>
      <td > 日本市场 </td>
      <td > 股票 </td>
      <td > LV2, LV3 </td>
    </tr>
</table>

  获取行情权限的方式参见 [行情权限](../intro/authority.html#2867) 

  注意：若账号拥有上述权限，但仍订阅失败，可能存在被其他终端 [踢掉行情权限](./opend.html#1228) 的情况。

## Q2：反订阅失败

A: 订阅至少一分钟后才能反订阅。

## Q3：反订阅成功但没释放额度

A: 所有连接都对该行情反订阅，才会释放额度。

举例：A 连接和 B 连接都在订阅 HK.00700 的摆盘，当 A 连接反订阅后，由于 B 连接仍在调用腾讯的摆盘数据，因此 OpenD 的额度不会释放，直至所有连接都反订阅 HK.00700 的摆盘。


## Q4：订阅不足一分钟关闭脚本连接，会释放额度吗？

A: 不会。连接关闭后，订阅时长不足一分钟的标的类型，会在达到一分钟后才自动反订阅，并释放相应的订阅额度。


## Q5：请求限频的具体限制逻辑是怎样？

A: 30 秒内最多 n 次，是指第 1 次和第 n+1 次请求间隔需要大于 30 秒。

## Q6：自选股添加不上是什么原因？

A: 请先检查是否有超出上限，或者删除一部分自选。

## Q7：为什么 API 端的美股报价和牛牛客户端的报价有不同？

A: 由于美股交易分散在很多家交易所，富途提供多种美股基本报价行情。 自4 月 16 日起，Futu API **免费开放**美股实时行情权限（推广期限免）。原需单独购买行情卡才可获取的深度摆盘美股行情，现已调整为免费。Futu API 会接入两种美股报价行情：Nasdaq Basic + TotalView（Nasdaq 交易所60档），NYSE Arcabook（Arca 60档）。     
如果您发现美股当天开盘价与客户端显示不一致，这是因为 Futu API 实时上游行情会综合 Nasdaq 和 NYSE Arcabook 数据。


## Q8：API 行情卡在哪里购买？

A:  
* 港股市场
  * [港股 LV2 高级行情（仅港澳台及海外 IP）](https://qtcardfthk.futufin.com/buy?market_id=1&amp;channel=2&amp;good_type=1#/)
  * [港股期权期货 LV2高级行情（仅港澳台及海外 IP）](https://qtcardfthk.futufin.com/buy?market_id=1&amp;channel=2&amp;good_type=8#/)
  * [港股 LV2 + 期权期货 LV2 行情（仅港澳台及海外 IP）](https://qtcardfthk.futufin.com/buy?market_id=1&amp;channel=2&amp;good_type=9#/)
  * [港股高级全盘行情（SF 行情）](https://qtcardfthk.futufin.com/buy?market_id=1&amp;channel=2&amp;good_type=10#/)
  
* 美股市场 (**限时推免**)
  * [Nasdaq Basic](https://qtcardfthk.futufin.com/buy?market_id=2&amp;channel=2&amp;good_type=12#/)
  * [Nasdaq Basic+TotalView (Non-Pro)](https://qtcardfthk.futufin.com/buy?market_id=2&good_type=18&channel=2#/)
  * [Nasdaq Basic+TotalView (Pro)](https://qtcardfthk.futufin.com/buy?market_id=2&good_type=19&channel=2#/)
  * [期权 OPRA 实时行情](https://qtcardfthk.futufin.com/buy?market_id=2&good_type=16&qtcard_channel=2#/)


## Q9：为什么有时候，获取实时数据的 get 接口响应比较慢？

A: 因为获取实时数据的 get 接口需要先订阅，并依赖后台给 OpenD 的推送。如果用户刚订阅就立刻用 get 接口请求，OpenD 有可能尚未收到后台推送。为了防止这种情况的发生，get 接口内置了等待逻辑，3 秒内收到推送会立刻返回给脚本，超过 3 秒仍未收到后台推送，才会给脚本返回空数据。  
涉及的 get 接口包括：get_rt_ticker、get_rt_data、get_cur_kline、get_order_book、get_broker_queue、get_stock_quote。因此，当发现获取实时数据的 get 接口响应比较慢时，可以先检查一下是否是无成交数据的原因。


## Q10：API 美股 Nasdaq 行情卡限免，可以获取哪些数据？

A: 自 4 月 16日起，Nasdaq Basic+TotalView 行情卡和 NYSE Arcabook 行情权限，将限时推免。您可免费获取的品类涵盖 Nasdaq、NYSE、NYSE MKT 交易所上市证券（包括美股正股和 ETF，不包括美股期货和美股期权）。    
支持的数据接口包括：快照，历史 K 线，实时逐笔订阅，实时一档摆盘订阅，实时 K 线订阅，实时报价订阅，实时分时订阅，到价提醒。


## Q11：各个行情品类的摆盘支持多少档？

A: 
行情品类|LV1|LV2|LV3|SF
:-|:-|:-|:-|:-
港股（含正股、窝轮、牛熊、界内证）|/|10|/|全盘+千笔明细
港股期权期货|1|10|/|/
美股（含 ETF）|1|60档|Nasdaq 60档+Arca 60档|/
美股期权|1|/|/|/
美股期货 |/|40档|/|/
A 股|5|/|/|/
新加坡股票|1|40|/|/
马来西亚股票|3|5|10|/
日本股票|/|10|40|/

## Q12：为什么我购买激活了行情卡之后，OpenD 仍然没有行情权限？

A:   
1. 由于 Futu API 的行情权限跟 APP 的行情权限不完全一样，部分行情卡仅适用于 APP 端。请先确认您所购买的行情卡是否是 OpenD 适用的。   
我们已将 Futu API 适用的 **所有** 行情卡列在《权限与限制》一节，请点击 [这里](/intro/authority.html#2867) 查看。
2. 行情卡购买激活成功后，是立即生效的。请 **重新启动 OpenD** 后，再次查看权限状态。


## Q13：如何通过订阅接口获取实时行情？
**第一步：订阅**  

将标的的代码和数据类型传入 [订阅接口](../quote/sub.md)，完成订阅。  

订阅接口支持了实时报价、实时摆盘、实时逐笔、实时分时、实时 K 线、实时经纪队列数据的获取。订阅成功后，OpenD 会持续收到富途服务器的实时数据推送。

注意：订阅额度会根据您的总资产、交易笔数和交易量，来进行分配，具体规则参见 [订阅额度 & 历史 K 线额度](../intro/authority.md#1314)。所以，如果您的订阅额度不足，可以先检查一下是否有无用的订阅在占用额度，及时 [反订阅](../quote/sub.md) 即可释放已占用的订阅额度。

**第二步：取数据**  

如何将订阅推送的数据从 OpenD 取回脚本呢？我们提供了如下两种方式：

**方式 1：实时数据回调**  
设置相应的回调函数，来异步处理 OpenD 收到的数据推送。  

设置好回调函数后，OpenD 会将收到的实时数据，立即推给脚本的回调函数进行处理。  

如果所订阅的标的比较活跃，此时的推送数据可能数据量较大且频率较高。如果您希望适当降低 OpenD 给脚本的推送频率，建议在 [OpenD 启动参数](../opend/opend-cmd.md#8799) 中配置 API 推送频率（`qot_push_frequency`）。  

方式 1 涉及的接口包括：[实时报价回调](../quote/update-stock-quote.md)、[实时摆盘回调](../quote/update-order-book.md)、[实时 K 线回调](../quote/update-kl.md)、[实时分时回调](../quote/update-rt.md)、[实时逐笔回调](../quote/update-ticker.md)、[实时经纪队列回调](../quote/update-broker.md)。

**方式 2：获取实时数据**  
通过获取实时数据接口，可以将 OpenD 收到的最新的数据，取回脚本。这种方式更加灵活，脚本不需要处理海量的推送。只要 OpenD 在持续接收富途服务器的推送，脚本可以随用随取，不用不取。  

由于是从 OpenD 接收的推送数据中取，所以这类接口没有频率限制。  

方式 2 涉及的接口包括：[获取实时报价](../quote/get-stock-quote.md)、[获取实时摆盘](../quote/get-order-book.md)、[获取实时 K 线](../quote/get-kl.md)、[获取实时分时](../quote/get-rt.md)、[获取实时逐笔](../quote/get-ticker.md)、[获取实时经纪队列](../quote/get-broker.md)。

## Q14：各个市场状态对应什么时间段？
A: 
<table>
    <tr>
        <th>市场</th>
        <th>品类</th>
        <th>市场状态</th>
        <th>时间段（当地时间）</th>
    </tr>
    <tr>
        <td rowspan="19" width = "15%">香港市场</td>
	    <td rowspan="8" width = "15%">证券类产品（含股票、ETFs、窝轮、牛熊、界内证）</td>
	    <td> * NONE：无交易</td>
      <td> CST 08:55 - 09:00</td>
    </tr>
    <tr>
	    <td >* AUCTION：盘前竞价</td>
      <td> CST 09:00 - 09:20</td>
    </tr>
    <tr>
	    <td >* WAITING_OPEN：等待开盘</td>
      <td> CST 09:20 - 09:30</td>
    </tr>
    <tr>
	    <td>* MORNING：早盘</td>
      <td> CST 09:30 - 12:00</td>
    </tr>
    <tr>
      <td>* REST: 午间休市</td>
	    <td>CST 12:00 - 13:00</td>
    </tr>
    <tr>
	    <td>* AFTERNOON：午盘</td>
      <td>CST 13:00 - 16:00</td>
    </tr>
    <tr>
	    <td>* HK_CAS：港股盘后竞价（港股市场增加 CAS 机制对应的市场状态）</td>
      <td>CST 16:00 - 16:08</td>
    </tr>
    <tr>
	    <td>* CLOSED：收盘</td>
      <td>CST 16:08 - 08:55（T+1）</td>
    </tr>
    <tr>
	    <td rowspan="5">期权、期货（仅日市）</td>
      <td>* NONE：期权待开盘</td>
      <td> CST 08:55 - 09:30</td>
    </tr>
    <tr>
	    <td>* MORNING：早盘</td>
      <td>CST 09:30 - 12:00</td>
    </tr>
    <tr>
      <td>* REST: 午间休市</td>
	    <td>CST 12:00 - 13:00</td>
    </tr>
    <tr>
	    <td>* AFTERNOON：午盘</td>
      <td>CST 13:00 - 16:00</td>
    </tr>
    <tr>
	    <td>* CLOSED：收盘</td>
      <td>CST 16:00 - 08:55（T+1）</td>
    </tr>
    <tr>
	    <td rowspan="6">期货（日夜市）</td>
      <td>* FUTURE_DAY_WAIT_FOR_OPEN：期货待开盘</td>
      <td rowspan="6"> 不同品种交易时间不同</td>
    </tr>
    <tr>
	    <td>* NIGHT_OPEN: 夜市交易时段</td>
    </tr>
    <tr>
	    <td>* NIGHT_END：夜市收盘</td>
    </tr>
    <tr>
	    <td>* FUTURE_DAY_WAIT_FOR_OPEN：期货待开盘</td>
    </tr>
    <tr>
	    <td>* FUTURE_DAY_OPEN：日市交易时段</td>
    </tr>
    <tr>
	    <td>* FUTURE_DAY_CLOSE：日市收盘</td>
    </tr>
  <tr>
        <td rowspan="16">美国市场</td>
	    <td rowspan="5">证券类产品（含股票、ETFs）</td>
	    <td>* PRE_MARKET_BEGIN：美股盘前交易时段</td>
      <td>EST 04:00 - 09:30</td>
    </tr>
    <tr>
	    <td>* AFTERNOON：美股持续交易时段</td>
      <td>EST 09:30 - 16:00</td>
    </tr>
    <tr>
	    <td>* AFTER_HOURS_BEGIN：美股盘后交易时段</td>
      <td>EST 16:00 - 20:00</td>
    </tr>
    <tr>
	    <td>* AFTER_HOURS_END：美股盘后收盘</td>
      <td>EST 20:00 - 04:00（T+1）</td>
    </tr>
    <tr>
	    <td>* OVERNIGHT：美股夜盘交易时段</td>
      <td>EST 20:00 - 04:00（T+1）</td>
    </tr>
    <tr>
	    <td rowspan="6">期权</td>
      <td>* NONE：期权待开盘</td>
      <td rowspan="6"> 不同品种交易时间不同</td>
    </tr>
    <tr>
	    <td>* REST：美指期权午间休市</td>
    </tr>
    <tr>
	    <td>* AFTERNOON：美股持续交易时段</td>
    </tr>
    <tr>
	    <td>* TRADE_AT_LAST：美指期权盘尾交易时段</td>
    </tr>
    <tr>
	    <td>* NIGHT：美指期权夜市交易时段</td>
    </tr>
    <tr>
	    <td>* CLOSED：收盘</td>
    </tr>
    <tr>
	    <td rowspan="5">期货</td>
      <td>* FUTURE_SWITCH_DATE：美期待开盘</td>
      <td rowspan="5"> 不同品种交易时间不同</td>
    </tr>
    <tr>
	    <td>* FUTURE_OPEN：美期交易时段</td>
     </tr>
     <tr>
	    <td>* FUTURE_BREAK：美期中盘休息</td>
     </tr>
     <tr>
	    <td>* FUTRUE_BREAK_OVER：美期休息后交易时段</td>
     </tr>
     <tr>
	    <td>* FUTURE_CLOSE：美期收盘</td>
     </tr>
    <tr>
        <td rowspan="7">A股市场</td>
	    <td rowspan="7">证券类产品（含股票、ETFs）</td>
	    <td>* NONE：无交易</td>
      <td>CST 08:55 - 09:15</td>
    </tr>
    <tr>
	    <td>* Auction：盘前竞价</td>
      <td>CST 09:15 - 09:25</td>
    </tr>
    <tr>
	    <td>* WAITING_OPEN：等待开盘</td>
      <td> CST 09:25 - 09:30</td>
    </tr>
    <tr>
	    <td>* MORNING：早盘</td>
      <td>CST 09:30 - 11:30</td>
    </tr>
    <tr>
	    <td>* REST：午间休市</td>
      <td>CST 11:30 - 13:00</td>
    </tr>
    <tr>
	    <td>* AFTERNOON：午盘</td>
      <td>CST 13:00 - 15:00</td>
    </tr>
    <tr>
	    <td>* CLOSED：收盘</td>
      <td>CST 15:00 - 08:55（T+1）</td>
    </tr>
    <tr>
        <td rowspan="10">新加坡市场</td>
	    <td rowspan="5">证券类产品（含股票、ETFs、REITs、结构性窝轮、DLCs）</td>
	    <td>* WAITING_OPEN：等待开盘</td>
      <td>CST 08:30 - 09:00</td>
    </tr>
    <tr>
	    <td>* MORNING：早盘</td>
      <td>CST 09:00 - 12:00</td>
    </tr>
     <tr>
	    <td>* REST: 午间休市</td>
      <td>CST 12:00 - 13:00</td>
    </tr>
     <tr>
	    <td>* AFTERNOON：午盘</td>
      <td>CST 13:00 - 17:00</td>
    </tr>
     <tr>
	    <td>* CLOSED：收盘</td>
      <td>CST 17:16 - 08:30（T+1）</td>
    </tr>
    <tr>
        <td rowspan="5">期货</td>
        <td>* FUTURE_DAY_WAIT_FOR_OPEN：期货待开盘</td>
        <td rowspan="5">不同品种交易时间不同</td>
      </tr>
     <tr>
	    <td>* NIGHT_OPEN：夜市交易时段</td>
    </tr>
     <tr>
	    <td>* NIGHT_END：夜市收盘</td>
    </tr>
     <tr>
	    <td>* FUTURE_DAY_OPEN：日市交易时段</td>
    </tr>
     <tr>
	    <td>* FUTURE_DAY_CLOSE：日市收盘</td>
    </tr>
    <tr>
        <td rowspan="10">日本市场</td>
      <td rowspan="5">证券类产品（含股票、ETFs）</td>
	    <td>* WAITING_OPEN：等待开盘</td>
      <td>JST 07:55 - 09:00</td>
    </tr>
    <tr>
	    <td>* MORNING：早盘</td>
      <td>JST 09:00 - 11:30</td>
    </tr>
     <tr>
	    <td>* REST: 午间休市</td>
      <td>JST 11:30 - 12:30</td>
    </tr>
     <tr>
	    <td>* AFTERNOON：午盘</td>
      <td>JST 12:30 - 15:30</td>
    </tr>
     <tr>
	    <td>* CLOSED：收盘</td>
      <td>JST 15:30 - 07:50（T+1）</td>
    </tr>
    <td rowspan="5">期货</td>
	    <td>* FUTURE_DAY_WAIT_FOR_OPEN：期货待开盘</td>
      <td>JST 16:25（T-1）- 16:30（T-1）</td>
    </tr>
     <tr>
	    <td>* NIGHT_OPEN：夜市交易时段</td>
      <td>JST 16:30（T-1） - 05:30</td>
    </tr>
     <tr>
	    <td>* NIGHT_END：夜市收盘</td>
      <td>JST 05:30 - 08:45</td>
    </tr>
     <tr>
	    <td>* FUTURE_DAY_OPEN：日市交易时段</td>
      <td>JST 08:45 - 15:15</td>
    </tr>
     <tr>
	    <td>* FUTURE_DAY_CLOSE：日市收盘</td>
      <td>JST 15:15 - 16:25</td>
    </tr>
    <tr>
        <td rowspan="5">马来西亚市场</td>
      <td rowspan="5">证券类产品（含股票、ETFs、REITs、窝轮）</td>
	    <td>* AUCTION：盘前竞价</td>
      <td>CST 08:30 - 09:00</td>
    </tr>
    <tr>
	    <td>* MORNING：早盘</td>
      <td>CST 09:00 - 12:30</td>
    </tr>
     <tr>
	    <td>* REST: 午间休市</td>
      <td>CST 12:30 - 14:00</td>
    </tr>
     <tr>
	    <td>* AFTERNOON：午盘</td>
      <td>CST 14:30 - 16:45</td>
    </tr>
     <tr>
	    <td>* CLOSED：收盘</td>
      <td>CST 17：00 - 08:25（T+1）</td>
    </tr>
    <tr>
        <td rowspan="3">加密货币市场</td>
	    <td rowspan="3">加密货币</td>
	    <td>* NONE：未交易</td>
      <td rowspan="3">不同币对可交易时间不同</td>
    </tr>
     <tr>
	    <td>* MORNING：早盘</td>
    </tr>
     <tr>
	    <td>* CLOSED：收盘</td>
    </tr>
</table>
\* CST, EST, JST 分别表示中国时间，美东时间，日本时间

## Q15：接口参数股票代码的格式

A：  
* 使用不同编程语言的用户，需要的股票代码的格式不同：
   * **Python 用户**  
    标的代码 code 使用 `exchange_market.symbol`格式，`exchange_market`表示交易所市场，`symbol`表示标的代码。支持订阅的标的如下：    

<table>
    <tr>
        <th>市场</th>
        <th>标的类别</th>
        <th>exchange_market</th>
        <th>example</th>
    </tr>
    <tr>
        <td rowspan="5">香港市场</td>
        <td>证券类产品（含股票、ETFs、窝轮、牛熊、界内证）</td>
        <td>HK</td>
        <td>腾讯控股：HK.00700</td>
    </tr>
    <tr>
        <td>指数</td>
        <td>HK</td>
        <td>恒生指数：HK.800000</td>
    </tr>  
    <tr>
        <td>期货</td>
        <td>HK</td>
        <td>恒指期货2606：HK.HSI2606</td>
    </tr>
    <tr>
        <td>期权</td>
        <td>HK</td>
        <td>* 股票期权 腾讯 260330 450.00购：HK.TCH260330C450000 <br> * 指数期权 恒指 260330 24000.00购：HK.HSI260330C24000000</td>
    </tr>
    <tr>
        <td>板块  (建议使用  get_plate_list 先获取板块列表) </td>
        <td>HK</td>
        <td>AI应用股：HK.LIST24037</td>
    </tr>
    <tr>
        <td rowspan="5">美国市场</td>
        <td>证券类产品（含纽交所、美交所、纳斯达克上市的股票、ETFs）</td>
        <td>US</td>
        <td>英伟达：US.NVDA</td>
    </tr>
    <tr>
        <td>期权</td>
        <td>US</td>
        <td>* 股票期权 NVDA 260330 160.00C：US.NVDA260330C160000 <br> * 指数期权 SPXW 260330 6330.00C: US..SPXW260330C6330000</td>
    </tr>
    <tr>
        <td>期货</td>
        <td>US</td>
        <td>标普500指数期货2606：US.ES2606</td>
    </tr>
    <tr>
        <td>板块  (建议使用  get_plate_list 先获取板块列表) </td>
        <td>US</td>
        <td>半导体精选：US.LIST20077</td>
    </tr>
    <tr>
        <td>指数（暂不支持获取）</td>
        <td>US</td>
        <td>标普500指数：US..SPX</td>
    </tr>
    <tr>
        <td rowspan="3">A股市场</td>
        <td>证券类产品（含股票、ETFs）</td>
        <td>SH/SZ</td>
        <td>贵州茅台：SH.600519</td>
    </tr>
    <tr>
        <td>指数</td>
        <td>SH/SZ</td>
        <td>上证指数：SH.000001</td>
    </tr>
    <tr>
        <td>板块  (建议使用  get_plate_list 先获取板块列表) </td>
        <td>SH/SZ</td>
        <td>汽车电子概念：SH.LIST0301</td>
    </tr>
    <tr>
        <td rowspan="2">新加坡市场</td>
        <td>证券类产品（含股票、ETFs、REITs、结构性窝轮、DLCs）</td>
        <td>SG</td>
        <td>新加坡航空公司：SG.C6L</td>
    </tr>
    <tr>
        <td>期货（暂不支持获取）</td>
        <td>SG</td>
        <td>A50指数期货2606：SG.CN2606</td>
    </tr>
    <tr>
        <td rowspan="2">日本市场</td>
        <td>证券类产品（含股票、ETFs）</td>
        <td>JP</td>
        <td>任天堂：JP.7974</td>
    </tr>
    <tr>
        <td>期货（暂不支持获取）</td>
        <td>JP</td>
        <td>大阪日经指数期货2606：JP.NK2252606</td>
    </tr>
    <tr>
        <td rowspan="1">马来西亚市场</td>
        <td>证券类产品（含股票、ETFs、REITs、窝轮）</td>
        <td>MY</td>
        <td>MAYBANK：MY.1155</td>
    </tr>
    <tr>
        <td rowspan="1">加密货币市场</td>
        <td>加密货币指数及币对</td>
        <td>CC</td>
        <td>* 指数：CC.BTC <br> * 可交易币对: CC.BTCUSD</td>
    </tr>
    </table>
      

   * **非 Python 用户**   
    股票结构参见 [Security](../quote/quote.html#1377)。   
    例如：腾讯控股，参数 market 传入 QotMarket_HK_Security，参数 code 传入'00700'。

* 查询方式：  
   通过 APP 查看代码和行情市场：行情 > 自选 > 全部。  
   行情市场定义，请参考 [这里](../quote/quote.html#427)。  
    ![code](../img/code.png)    


## Q16：复权因子相关
A：  
### 概述
所谓 [复权](../quote/get-rehab.html#770) 就是对股价和成交量进行权息修复，按照股票的实际涨跌绘制股价走势图，并把成交量调整为相同的股本口径。  
公司行动（如：拆股、合股、送股、转增股、配股、增发股、分红）均可能对股价产生影响，而复权计算可对量价进行调整，剔除公司行动的影响，保持股价走势的连续性。   

### 名词解释
- 公司行动：上市公司进行一些股权、股票等影响公司股价和股东持仓变化的行为。
- 前复权：保持现有的股价不变，以当前的股价为基准，对以前的股价进行复权计算。
- 后复权：保持先前的股价不变，以过去的股价为基准，对以后的股价进行复权计算。
- 复权因子：即权息修复比例，用于计算复权后的价格及持仓数量。
- 除权除息日：即股权登记日下一个交易日。在股票的除权除息日，证券交易所都要计算出股票的除权除息价，以作为股民在除权除息日开盘的参考。其意义是股票股利分配给股东的日期。

### 复权方法
主流的复权计算方法分为两种：事件法和连乘法；而 Futu API 针对不同市场使用不同的计算方法。
- 事件复权法：通过还原除权除息的各类事件进行复权；存在两个复权因子（复权因子 A 和 复权因子 B），复权因子 B 主要调整现金分红对股价的影响，而复权因子 A 调整其他公司行动对股价的影响。
- 连乘复权法：通过复权因子连乘的方式进行复权，只保留 复权因子 A（或将 复权因子 B 置为0），复权因子 A 为 除权除息日前收盘价/该日经权息调整后的前收盘价。

::: tip 提示
*  API 对美股前复权使用连乘法，即将 复权因子 B 置为0。  
*  API 对除美股以外的标的（A股、港股、新加坡股票等）及美股后复权使用事件法。  
:::

### 计算公式
#### 单次复权
- 前复权：  
前复权价格 = 不复权价格 × 前复权因子 A + 前复权因子 B   
- 后复权：  
后复权价格 = 不复权价格 × 后复权因子 A + 后复权因子 B

#### 多次复权
- 前复权：按照时间顺序，筛选出大于计算日期的复权因子，优先使用时间较早的复权因子进行复权计算。以两次复权为例： 

  ![code](../img/forward_fomula.png)    
- 后复权：按照时间倒序，筛选出小于等于计算日期的复权因子，优先使用时间较晚的复权因子进行复权计算。以两次复权为例： 

  ![code](../img/backward_fomula.png)    

### 示例
#### 单次前复权示例
以牧原股份为例：
- 筛选复权因子如下：  

除权除息日|股票代码|方案说明|前复权因子 A |前复权因子 B 
:-|:-|:-|:-|:-
2021/06/03|SZ.002714|10转4.0股派14.61元（含税）|0.71429|-1.04357

- 不复权数据如下：  

日期|股票代码|不复权收盘价
:-|:-|:-
2021/06/02|SZ.002714|93.11
2021/06/03|SZ.002714|66.25

- 前复权数据如下：  

日期|股票代码|前复权收盘价
:-|:-|:-
2021/06/02|SZ.002714|65.4639719
2021/06/03|SZ.002714|66.25

- 前复权数据计算方法：  
牧原股份在 2021/06/03 进行拆股及现金分红行动（10转4.0股派14.61元），根据前复权计算公式对 2021/06/02 的收盘价进行调整计算，则：前复权价格（65.4639719） = 不复权价格（93.11） × 前复权因子 A（0.71429） + 前复权因子 B（-1.04357）   

  ![code](../img/forward_example.png)    

#### 多次后复权示例
接上一个例子，计算牧原股份在 2021/06/02 的后复权价格：
- 筛选复权因子如下：  

除权除息日|股票代码|方案说明|后复权因子 A |后复权因子 B 
:-|:-|:-|:-|:-|
2014/07/04|SZ.002714|10派2.34元（含税）|1|0.234
2015-06-10|SZ.002714|10转10.0股派0.61元（含税）|2|0.061
2016-07-08|SZ.002714|10转10.0股派3.53元（含税）|2|0.353
2017-07-11|SZ.002714|10转8.0股派6.9元（含税）|1.8|0.69
2018-07-03|SZ.002714|10派6.91元（含税）|1|0.691
2019-07-04|SZ.002714|10派0.5元（含税）|1|0.05
2020-06-04|SZ.002714|10转7.0股派5.5元（含税）|1.7|0.55

- 不复权数据如下：  

日期|股票代码|不复权收盘价
:-|:-|:-
2021/06/02|SZ.002714|93.11

- 后复权数据如下：  

日期|股票代码|后复权收盘价
:-|:-|:-
2021/06/02|SZ.002714|1152.7226

- 后复权数据计算方法：  
为了计算牧原股份在 2021/06/02 的后复权价格，需要将早于 2021/06/02 的复权事件进行一一复权，得到最后的后复权价格，具体计算如下：

![code](../img/backward_example.jpg)

## Q17：加密货币多券商行情相关

#### 1. 为什么加密货币行情会因券商不同而有所差异？
A：由于各券商对接的行情上游不同，同一币对在不同券商下可能存在行情数据差异。API支持根据券商切换行情数据源（OpenQuoteContext 指定 security_firm），确保您看到的行情与实际交易一致。

#### 2. 如果我没有指定券商，会展示哪个数据源的行情？
A：未指定券商时，API默认返回您的主推券商行情上游数据。

#### 3. 我有多个券商账户都支持加密货币交易，应该如何选择？
A：建议选择您实际交易账户所对应的券商来获取行情。这样可以确保所见行情与下单时的撮合价格一致，避免因行情数据源不同导致的价格偏差。

---

# 交易相关

## Q1：模拟交易相关

A:
### 概述
模拟交易是在真实的市场环境中，用虚拟资金做交易，不会对您的真实账户的资产造成影响。

#### 交易时间
模拟交易支持的时段：常规交易时段（所有市场）、美股盘中时段、美股盘前盘后时段（仅美股融资融券模拟账户支持）   
模拟交易不支持的时段：美股夜盘时段、A股竞价时段、港股竞价时段    
详情可点击 [模拟交易规则](https://support.futunn.com/topic692)


#### 支持品类
Futu API 支持模拟交易的品类请参考 [这里](../intro/intro.md#1396)。

#### 解锁
与真实交易不同，模拟交易无需对账户进行解锁，即可下单或改单撤单。


#### 订单
1. 订单类型：限价单和市价单。  
2. 改单操作类型：模拟交易不支持使生效、使失效、删除，仅支持修改订单、 撤单。  
3. 成交：模拟交易不支持成交相关操作，包括 [查询今日成交](../trade/get-order-fill-list.md#2621)、[查询历史成交](../trade/get-history-order-fill-list.md#9015)、[响应成交推送回调](../trade/update-order-fill.md#210)。
4. 有效期限：模拟交易有效期限仅支持当日有效。
5. 卖空：期权和期货支持卖空。股票仅美股支持卖空。 
6. 模拟交易账户不支持查询订单费用。
7. 模拟交易账户不支持查询现金流水。
8. 在组合期权订单场景下，支持持仓查询，暂不支持组合订单查询。

#### 操作平台
1. 移动端：我的 — 模拟交易  

![sim-page](../img/sim-page.png)

2. 桌面端：左侧模拟 tab  

![sim-page](../img/create-sim-account.png)


3. 网页端：[模拟交易界面](https://m-match.futunn.com/simulate/)

4. Futu API：在调用接口时，设置参数交易环境为模拟环境即可。详见 [如何使用 Futu API 进行模拟交易](../qa/trade.md#8728)。

::: tip 提示
* 以上四种方式只是操作平台不同，四种方式操作的模拟账户是共通的。  
:::


### 如何使用 Futu API 进行模拟交易？

#### 创建连接
先根据交易品种 [创建相应的连接](../trade/base.md#7902) 。当交易品种是股票或期权时，请使用 `OpenSecTradeContext`。当交易品种是期货时，请使用 `OpenFutureTradeContext`。

#### 获取交易业务账户列表
使用 [获取交易业务账户列表](../trade/get-acc-list.md#5754) 查看交易账户（包括模拟账户、真实账户）。以 Python 为例：返回字段交易环境 `trd_env` 为 `SIMULATE`，表示模拟账户。   
获取港股模拟交易账户，需要指定 filter_trdmarket 为 TrdMarket.HK，此时会返回2个模拟交易账号。其中 sim_acc_type = STOCK 为港股模拟账户，sim_acc_type = OPTION 为港股期权模拟账户，sim_acc_type = FUTURES 为港股期货模拟账户。   
获取美股模拟交易账户，需要指定 filter_trdmarket 为 TrdMarket.US，sim_acc_type = STOCK_AND_OPTION 代表美股融资融券模拟账户，可以模拟交易股票和期权。sim_acc_type = FUTURES 为美国期货模拟账户。    

* **Example：Stocks and Options**
```python
from futu import *
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
#trd_ctx = OpenFutureTradeContext(host='127.0.0.1', port=11111, is_encrypt=None, security_firm=SecurityFirm.FUTUSECURITIES)
ret, data = trd_ctx.get_acc_list()
if ret == RET_OK:
    print(data)
    print(data['acc_id'][0])  # get the first account id
    print(data['acc_id'].values.tolist())  # convert to list format
else:
    print('get_acc_list error: ', data)
trd_ctx.close()
```

* **Output**
```python
               acc_id   trd_env acc_type          card_num   security_firm  \
0  281756480572583411      REAL   MARGIN  1001318721909873  FUTUSECURITIES   
1             9053218  SIMULATE     CASH               N/A             N/A   
2             9048221  SIMULATE   MARGIN               N/A             N/A   

  sim_acc_type  trdmarket_auth  
0          N/A  [HK, US, HKCC]  
1        STOCK            [HK]  
2       OPTION            [HK] 
```
::: tip 提示
* 模拟交易中，区分股票账户和期权账户，股票账户只能交易股票，期权账户只能交易期权；以 Python 为例：返回字段中模拟账户类型 `sim_acc_type` 为 `STOCK`，表示股票账户；为`OPTION`，表示期权账户。
::: 

* **Example: Futures**
```python
from futu import *
#trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
trd_ctx = OpenFutureTradeContext(host='127.0.0.1', port=11111, is_encrypt=None, security_firm=SecurityFirm.FUTUSECURITIES)
ret, data = trd_ctx.get_acc_list()
if ret == RET_OK:
    print(data)
    print(data['acc_id'][0])  # get the first account id
    print(data['acc_id'].values.tolist())  # convert to list format
else:
    print('get_acc_list error: ', data)
trd_ctx.close()
```

* **Output**
```python
    acc_id   trd_env acc_type card_num security_firm sim_acc_type  \
0  9497808  SIMULATE   MARGIN      N/A           N/A      FUTURES   
1  9497809  SIMULATE   MARGIN      N/A           N/A      FUTURES   
2  9497810  SIMULATE   MARGIN      N/A           N/A      FUTURES   
3  9497811  SIMULATE   MARGIN      N/A           N/A      FUTURES   

          trdmarket_auth  
0  [FUTURES_SIMULATE_HK]  
1  [FUTURES_SIMULATE_US]  
2  [FUTURES_SIMULATE_SG]  
3  [FUTURES_SIMULATE_JP]  
```  

#### 下单
使用 [下单接口](../trade/place-order.md) 时，设置交易环境为模拟环境即可。以 Python 为例：`trd_env = TrdEnv.SIMULATE`。

* **Example**
```python
from futu import *
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
ret, data = trd_ctx.place_order(price=510.0, qty=100, code="HK.00700", trd_side=TrdSide.BUY, trd_env=TrdEnv.SIMULATE)
if ret == RET_OK:
    print(data)
else:
    print('place_order error: ', data)
trd_ctx.close()
```
* **Output**
```python
	code	stock_name	trd_side	order_type	order_status	order_id	qty	price	create_time	updated_time	dealt_qty	dealt_avg_price	last_err_msg	remark	time_in_force	fill_outside_rth
0	HK.00700	腾讯控股	BUY	NORMAL	SUBMITTING	4642000476506964749	100.0	510.0	2021-10-09 11:34:54	2021-10-09 11:34:54	0.0	0.0			DAY	N/A
```

#### 撤单改单
使用 [撤单接口](../trade/modify-order.md) 时，设置交易环境为模拟环境即可。以 Python 为例： `trd_env = TrdEnv.SIMULATE`。

* **Example**
```python
from futu import *
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
order_id = "4642000476506964749"
ret, data = trd_ctx.modify_order(ModifyOrderOp.CANCEL, order_id, 0, 0, trd_env=TrdEnv.SIMULATE)
if ret == RET_OK:
    print(data)
else:
    print('modify_order error: ', data)
trd_ctx.close()
```
* **Output**
```python
    trd_env             order_id
0  SIMULATE  4642000476506964749
```

#### 查询历史订单
使用 [查询历史订单接口](../trade/get-history-order-list.md) 时，设置交易环境为模拟环境即可。以 Python 为例：`trd_env = TrdEnv.SIMULATE`。

* **Example**
```python
from futu import *
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
ret, data = trd_ctx.history_order_list_query(trd_env=TrdEnv.SIMULATE)
if ret == RET_OK:
    print(data)
else:
    print('history_order_list_query error: ', data)
trd_ctx.close()
```
* **Output**
```python
	code	stock_name	trd_side	order_type	order_status	order_id	qty	price	create_time	updated_time	dealt_qty	dealt_avg_price	last_err_msg	remark	time_in_force	fill_outside_rth
0	HK.00700	腾讯控股	BUY	ABSOLUTE_LIMIT	CANCELLED_ALL	4642000476506964749	100.0	510.0	2021-10-09 11:34:54	2021-10-09 11:37:08	0.0	0.0			DAY	N/A
```

### 如何重置模拟账户？
目前 Futu API 不支持重置模拟账户，您可在移动端使用复活卡重置指定模拟账户，重置后账户资金将恢复至初始值，历史订单将会被清空。

#### 具体操作
移动端：我的 — 模拟交易 — 我的头像 — 我的道具 — 复活卡。
![sim-page](../img/sim-reset.png)


## Q2：是否支持 A 股交易？

A: 模拟交易支持 A 股交易。但真实交易仅可通过 A 股通交易部分 A 股，具体详见 [A 股通名单](https://www.hkex.com.hk/Mutual-Market/Stock-Connect/Eligible-Stocks/View-All-Eligible-Securities?sc_lang=zh-HK)。

## Q3：各市场支持的交易方向

A: 除了期货，其他股票都只支持传入 BUY 和 SELL 两个交易方向。在空仓情况下传入 SELL，产生的订单交易方向是卖空。

## Q4：真实交易中，各市场支持的订单类型

A: 
<table style="font-size:14px;">
    <tr>
        <th>市场</th>
        <th>品种</th>
        <th>限价单</th>
        <th>市价单</th>
        <th>竞价限价单</th>
        <th>竞价市价单</th>
        <th>绝对限价单</th>
        <th>特别限价单</th>
        <th>特别限价且要求<br/>全部成交订单</th>
        <th>止损市价单</th>
        <th>止损限价单</th>
        <th>触及市价单（止盈）</th>
        <th>触及限价单（止盈）</th>
        <th>跟踪止损市价单</th>
        <th>跟踪止损限价单</th>
    </tr>
    <tr>
        <td rowspan="3">香港市场</td>
        <td>证券类产品（含股票、ETFs、<br/>窝轮、牛熊、界内证）</td>
        <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td>
    </tr>
    <tr>
        <td>期权</td>
        <td>✓</td> <td>X</td> <td>-</td> <td>-</td> <td>-</td> <td>-</td> <td>-</td> <td>X</td> <td>✓</td> <td>X</td> <td>✓</td> <td>X</td> <td>✓</td>
    </tr>
    <tr>
        <td>期货</td>
        <td>✓</td> <td>✓</td> <td>-</td> <td>✓</td> <td>-</td> <td>-</td> <td>-</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td>
    </tr>
    <tr>
        <td rowspan="3">美国市场</td>
        <td>证券类产品（含股票、ETFs）</td>
        <td>✓</td> <td>✓</td> <td>-</td> <td>-</td> <td>-</td> <td>-</td> <td>-</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td>
    </tr>
    <tr>
        <td>期权</td>
        <td>✓</td> <td>✓</td> <td>-</td> <td>-</td> <td>-</td> <td>-</td> <td>-</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td>
    </tr>
    <tr>
        <td>期货</td>
        <td>✓</td> <td>✓</td> <td>-</td> <td>-</td> <td>-</td> <td>-</td> <td>-</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td>
    </tr>
    <tr>
        <td>A 股通市场</td>
        <td>证券类产品（含股票、ETFs）</td>
        <td>✓</td> <td>X</td> <td>-</td> <td>-</td> <td>-</td> <td>-</td> <td>-</td> <td>X</td> <td>✓</td> <td>X</td> <td>✓</td> <td>X</td> <td>✓</td>
    </tr>
    <tr>
        <td>新加坡市场</td>
        <td>期货</td>
        <td>✓</td> <td>✓</td> <td>-</td> <td>-</td> <td>-</td> <td>-</td> <td>-</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td>
    </tr>
    <tr>
        <td>日本市场</td>
        <td>期货</td>
        <td>✓</td> <td>✓</td> <td>-</td> <td>-</td> <td>-</td> <td>-</td> <td>-</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td> <td>✓</td>
    </tr>
</table>


## Q5：各市场支持的订单操作

A: 
* 港股支持改单、撤单、生效、失效、删除
* 美股仅支持改单和撤单
* A 股通仅支持撤单
* 期货支持改单、撤单、删除

## Q6：OpenD 启动参数 future_trade_api_time_zone 如何使用？

A：由于期货账户支持交易的品种分布在全球多个交易所，交易所的所属时区各有不同，因此期货交易 API 的时间显示就成为了一个问题。  
OpenD 启动参数中新增了 future_trade_api_time_zone 这一参数，供全球不同地区的期货交易者灵活指定时区。默认时区为 UTC+8，如果您更习惯美东时间，只需将此参数配置为 UTC-5 即可。
::: tip  提示
+ 此参数仅会对期货交易接口类对象生效。港股交易、美股交易、A 股通交易接口类对象的时区，仍然按照交易所所在的时区进行显示。
+ 此参数会影响的接口包括：响应订单推送回调，响应成交推送回调，查询今日订单，查询历史订单，查询当日成交，查询历史成交，下单。
:::

## Q7：通过 API 下的订单，能在 APP 上面看到吗？
A：可以看到。  
通过 Futu API 成功发出下单指令后，您可以在 APP 的 **交易** 页面，查看今日订单、订单状态、成交情况等等，也可以在 **消息—订单消息** 中收到成交提醒的通知。

## Q8：哪些品类支持在非交易时段下单？
A：所有的订单，都需要在开盘期间才能够成交。  
Futu API 仅对一部分品类，支持了 **非交易时段下单** 的功能（APP 上支持更多品类的非交易时段下单功能）。具体请参考下表：

<table>
    <tr>
        <th rowspan="2">市场</th>
        <th rowspan="2">标的类型</th>
        <th rowspan="2">模拟交易</th>
        <th colspan="7">真实交易</th>
    </tr>
    <tr>
        <th>Futu HK</th>
        <th>Moomoo US</th>
        <th>Moomoo SG</th>
        <th>Moomoo AU</th>
        <th>Moomoo MY</th>
        <th>Moomoo CA</th>
        <th>Moomoo JP</th>
    </tr>
    <tr>
        <td rowspan="3">香港市场</td>
	    <td>股票、ETFs、窝轮、牛熊、界内证</td>
	    <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
   <tr>
	    <td>期权 (含指数期权，需使用期货账户交易)</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
	    <td>期货</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
        <td rowspan="3">美国市场</td>
	    <td>股票、ETFs</td>
	    <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
    </tr>
    <tr>
        <td>期权</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
    </tr>
   <tr>
	    <td>期货</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
        <td rowspan="2">A 股市场</td>
	    <td>A 股通股票</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
     <tr>
	    <td>非 A 股通股票</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
   <tr>
        <td rowspan="2">新加坡市场</td>
	    <td>股票、ETFs、窝轮、REITs、DLCs</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
	    <td>期货</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
	    <td rowspan="2">日本市场</td>
        <td>股票、ETFs、REITs</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
        <td>期货</td>
        <td align="center">✓</td>
        <td align="center">✓</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
	    <td rowspan="1">澳大利亚市场</td>
        <td>股票、ETFs</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
    <tr>
	    <td rowspan="1">加拿大市场</td>
        <td>股票</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
        <td align="center">X</td>
    </tr>
</table>
::: tip 提示
- ✓：支持非交易时段下单
- X：暂不支持非交易时段下单（或暂不支持交易）
:::

## Q9：对于下单接口，各订单类型对应的必传参数以及券商对单笔订单的下单限制
A1: 各订单类型对应的必传参数

<table style="font-size:14px;">
    <tr>
        <th>参数</th>
        <th>限价单</th>
        <th>市价单</th>
        <th>竞价限价单</th>
        <th>竞价市价单</th>
        <th>绝对限价单</th>
        <th>特别限价单</th>
        <th>特别限价且要求<br/>全部成交订单</th>
        <th>止损市价单</th>
        <th>止损限价单</th>
        <th>触及市价单（止盈）</th>
        <th>触及限价单（止盈）</th>
        <th>跟踪止损市价单</th>
        <th>跟踪止损限价单</th>
    </tr>
    <tr>
        <td>price</td>
        <td>✓</td> <td></td> <td>✓</td> <td> </td> <td>✓</td> <td>✓</td> <td>✓</td>  <td></td><td>✓</td> <td></td> <td>✓</td><td> </td><td> </td>
    </tr>
    <tr>
        <td>qty</td>
        <td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td>
    </tr>
    <tr>
        <td>code</td>
        <td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td>
    </tr>
    <tr>
        <td>trd_side</td>
        <td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td>
    </tr>
    <tr>
        <td>order_type</td>
        <td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td>
    </tr>
    <tr>
        <td>trd_env</td>
        <td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td>
    </tr>
    <tr>
        <td>aux_price</td>
        <td></td> <td></td> <td></td> <td></td> <td></td> <td></td> <td> </td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td> </td><td> </td>
    </tr>
    <tr>
        <td>trail_type</td>
        <td></td> <td></td> <td></td> <td></td> <td></td> <td></td> <td> </td><td> </td><td> </td><td> </td><td> </td> <td>✓</td><td>✓</td>
    </tr>
    <tr>
        <td>trail_value</td>
        <td></td> <td></td> <td></td> <td></td> <td></td> <td></td> <td> </td><td> </td><td> </td><td> </td><td> </td> <td>✓</td><td>✓</td>
    </tr>
    <tr>
        <td>trail_spread</td>
        <td></td> <td></td> <td></td> <td></td> <td></td> <td></td> <td> </td><td> </td><td> </td><td> </td><td> </td> <td> </td><td>✓</td>
    </tr>
</table>

`Python 用户` 注意，[place_order](../trade/place-order.html#4080) 并未对 price 设置默认值，对于上述五类订单类型，仍需对 price 传参，price 可以传入任意值。

A2：各券商对单笔订单的股数及金额限制
<table style="font-size:14px;">
    <tr>
        <th>券商</th>
        <th>品类</th>
        <th>单笔订单股数上限</th>
        <th>单笔订单金额上限</th>
    </tr>
    <tr>
        <td rowspan="3">FUTU HK</td>
        <td>A股通</td>
        <td>1,000,000 股</td>
        <td>￥5,000,000</td>
    </tr>
    <tr>
        <td>美股</td>
        <td>500,000 股</td>
        <td>$5,000,000</td>
    </tr>
    <tr>
        <td>香港股票期货/期权</td>
        <td>3,000 手</td>
        <td>无限制</td>
    </tr>
    <tr>
        <td>moomoo US</td>
        <td>美股</td>
        <td>500,000 股</td>
        <td>$10,000,000</td>
    </tr>
    <tr>
        <td>moomoo SG</td>
        <td>美股</td>
        <td>500,000 股</td>
        <td>$5,000,000</td>
    </tr>
    <tr>
        <td>moomoo AU</td>
        <td>美股</td>
        <td>无限制</td>
        <td>无限制</td>
    </tr>
</table>


## Q10：对于改单接口，修改订单时，各订单类型对应的必传参数
A: 

<table style="font-size:14px;">
    <tr>
        <th>参数</th>
        <th>限价单</th>
        <th>市价单</th>
        <th>竞价限价单</th>
        <th>竞价市价单</th>
        <th>绝对限价单</th>
        <th>特别限价单</th>
        <th>特别限价且要求<br/>全部成交订单</th>
        <th>止损市价单</th>
        <th>止损限价单</th>
        <th>触及市价单（止盈）</th>
        <th>触及限价单（止盈）</th>
        <th>跟踪止损市价单</th>
        <th>跟踪止损限价单</th>
    </tr>
    <tr>
        <td>modify_order_op</td>
        <td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td>
    </tr>
    <tr>
        <td>order_id</td>
        <td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td>
    </tr>
    <tr>
        <td>price</td>
        <td>✓</td> <td></td> <td>✓</td> <td> </td> <td>✓</td> <td>✓</td> <td>✓</td>  <td></td><td>✓</td> <td></td> <td>✓</td><td> </td><td> </td>
    </tr>
    <tr>
        <td>qty</td>
        <td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td>
    </tr>
    <tr>
        <td>trd_env</td>
        <td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td>✓</td><td>✓</td>
    </tr>
    <tr>
        <td>aux_price</td>
        <td></td> <td></td> <td></td> <td></td> <td></td> <td></td> <td> </td><td>✓</td><td>✓</td><td>✓</td><td>✓</td> <td> </td><td> </td>
    </tr>
    <tr>
        <td>trail_type</td>
        <td></td> <td></td> <td></td> <td></td> <td></td> <td></td> <td> </td><td> </td><td> </td><td> </td><td> </td> <td>✓</td><td>✓</td>
    </tr>
    <tr>
        <td>trail_value</td>
        <td></td> <td></td> <td></td> <td></td> <td></td> <td></td> <td> </td><td> </td><td> </td><td> </td><td> </td> <td>✓</td><td>✓</td>
    </tr>
    <tr>
        <td>trail_spread</td>
        <td></td> <td></td> <td></td> <td></td> <td></td> <td></td> <td> </td><td> </td><td> </td><td> </td><td> </td> <td> </td><td>✓</td>
    </tr>
</table>

`Python 用户` 注意，[modify_order](../trade/modify-order.html#7408) 并未对 price 设置默认值，对于上述五类订单类型，仍需对 price 传参，price 可以传入任意值。

## Q11：交易接口返回“当前证券业务账户尚未同意免责协议”？
A：  
点击下方链接完成协议确认，重启 OpenD 即可正常使用交易功能。
所属券商|协议确认
:-|:-|:-
FUTU HK|[点击这里](https://risk-disclosure.futuhk.com/index?agreementNo=HKOT0015)
Moomoo US|[点击这里](https://risk-disclosure.us.moomoo.com/index?agreementNo=USOT0027)
Moomoo SG|[点击这里](https://risk-disclosure.sg.moomoo.com/index?agreementNo=SGOT0015)
Moomoo AU|[点击这里](https://risk-disclosure.au.moomoo.com/index?agreementNo=AUOT0025)
Moomoo CA|[点击这里](https://risk-disclosure.ca.moomoo.com/index?agreementNo=CAOT0117)
Moomoo MY|[点击这里](https://risk-disclosure.my.moomoo.com/index?agreementNo=MYOT0066)
Moomoo JP|[点击这里](https://risk-disclosure.jp.moomoo.com/index?agreementNo=JPOT0140)


## Q12：典型日内交易者（PDT）相关

### 概述

客户使用moomoo证券(美国) 账户进行日内交易时，会受到美国 FINRA 的监管限制（此为美国券商受到的监管要求，与交易股票的所属市场无关。其他国家或地区的券商  (如：富途证券(香港)、moomoo证券(新加坡)) 的交易账户则不受此限制）。若用户在任意连续的5个交易日内，进行日内交易 3 次以上，则会被标记为典型日内交易者（PDT）。  
更多详情，[点击这里](https://fastsupport.fututrade.com/hans/category11014/scid11017)

### 进行日内交易的流程图
![PDT_process](../img/PDT_process.png) 

### 我愿意被标记为 PDT，且不希望程式交易被打断，如何关闭“防止被标记为 PDT”？
A：  
当您在连续的 5 个交易日内，进行第 4 次日内交易时，为了防止您被无意识地标记为 PDT，服务器会对此交易进行拦截。若您主动想被标记为 PDT，并且不希望服务器拦截，可以采取以下措施：  
在 [命令行 OpenD 中配置参数](../opend/opend-cmd.html#8799)，将启动参数 `pdt_protection` 的值修改为 0，以关闭“防止被标记为日内交易者”的功能。

![US_para](../img/US_para.png)  
注意：若您被标记 PDT，当您的账户权益小于$25000时，您将无法开仓。

### 如何关闭 DTCall 预警提醒？
A：  
您被标记为 PDT 后，需要留意账户的日内交易购买力（DTBP），日内交易超出 DTBP 时将收到日内交易保证金追缴（DTCall）。服务器会在您即将开仓下单超出剩余日内交易购买力前，阻止您的下单。若您仍然希望进行下单，并且不希望服务器拦截，可以采取以下措施：    
在 [命令行 OpenD 中配置参数](../opend/opend-cmd.html#8799)，将启动参数 `dtcall_confirmation` 的值修改为 0，以关闭“日内交易保证金追缴预警”的功能。

![US_para2](../img/US_para2.png)  
注意：若您开仓订单的市值大于您的剩余日内交易购买力，并且在今日平仓当前标的，您将会收到日内交易保证金追缴通知（Day-Trading Call），只能通过存入资金才能解除。

### 如何查看 DTBP 的值？
A：  
通过 [查询账户资金](../trade/get-funds.html#4346) 接口，可以获取日内交易相关的返回值，如：剩余日内交易次数、初始日内交易购买力、剩余日内交易购买力等。


## Q13：如何跟踪订单成交状态
A:
下单后，可使用以下接口跟踪订单成交状态：
<table>
    <tr>
      <th> 交易环境 </th>
      <th> 接口 </th>
    </tr>
    <tr>
      <td > 真实交易 </td>
      <td > [响应订单推送回调](../trade/update-order.html)，[响应成交推送回调](../trade/update-order-fill.html) </td>
    </tr>
    <tr>
	  <td> 模拟交易</td>
      <td> [响应订单推送回调](../trade/update-order.html)</td>
    </tr>
</table>

注意：对于非 python 语言用户，在使用上述两个接口之前，需要先进行 [订阅交易推送](../trade/sub-acc-push.html)

#### 响应订单推送回调 的特点：
反馈 整个订单 的信息变动。当以下 8 个字段发生变化时，会触发订单推送：  
`订单状态`，`订单价格`，`订单数量`，`成交数量`，`触发价格`，`跟踪类型`，`跟踪金额/百分比`，`指定价差`  

因此，当您进行下单、改单，撤单、使生效、使失效操作，或者订单在市场中发生了高级订单被触发、有成交变动的情况，都会触发订单推送。您只需要调用 [响应成交推送回调](../trade/update-order-fill.html)，即可监听这些信息。

#### 响应成交推送回调 的特点：
只反馈 单笔成交 的信息。当以下 1 个字段发生变化时，会触发订单推送：  
`成交状态`  

举例：假设一笔限价单订单 900 股，分成了 3 次才完全成交，每次成交分别是：200、300、400 股。  
![example](../img/example.png)


## Q14：下单接口返回“此产品最小单位为 xxx，请调整至最小单位的整数倍后再提交”？
A:  
对于不同市场的标的，交易所有着不同的最小变动单位要求。如果提交的订单价格不符合要求，订单将会被拒绝。各市场价位规则如下：  

### 价位规则
#### 香港市场

以港交所官方说明为准，点击 [这里](https://www.futufin.com/hans/support/topic605?lang=zh-cn)。


#### A 股市场
股票价位：0.01。

#### 美国市场
股票价位：
<table>
    <tr>
      <th> 合约价格 </th>
      <th> 价位 </th>
    </tr>
    <tr>
      <td > $1 以下 </td>
      <td > $0.0001 </td>
    </tr>
    <tr>
	  <td> $1 以上</td>
      <td> $0.01 </td>
    </tr>
</table>

期权价位：
<table>
    <tr>
      <th> 合约价格 </th>
      <th> 价位 </th>
    </tr>
    <tr>
      <td > $0.10 - $3.00 </td>
      <td > $0.01 或者 $0.05</td>
    </tr>
    <tr>
	  <td> $3.00 以上</td>
      <td> $0.05 或者 $0.10</td>
    </tr>
</table>

期货价位：不同合约价位规则不同。可以通过 [获取期货合约资料](../quote/get-future-info.html#7447) 接口的返回字段 `最小变动的单位` 查看。

### 怎么避免订单价格不在价位上？
* 方法一：通过 [获取实时摆盘](../quote/get-order-book.html) 接口，获取合法的交易价格。交易所摆盘上的价位一定是合法的价位。  
* 方法二：通过 [下单](../trade/place-order.html) 接口的参数 `价格微调幅度`，将传入价格自动调整到合法的交易价格上。  

   例如：假设腾讯控股当前市价为 359.600，根据价位规则，对应的最小变动价位为 0.200。  

   假设您的下单传入订单价格为 359.678，价格微调幅度为 0.0015，代表接受 OpenD 对传入价格自动向上调整到最近的合法价位，且不能超过 0.15%。此情景下，向上最近的合法价格为 359.800，价格实际需要调整的幅度为 0.034%，符合价格微调幅度的要求，因此最终提交的订单价格为 359.800。  

   若价格微调幅度设置数值小于实际需要调整的幅度，OpenD 自动调整价位失败，订单仍会返回报错“订单价格不在价位上”。


## Q15：我的购买力足够，为什么下市价单会返回“购买力不足”？
A：
### 为什么市价单会提示购买力不足  
- 出于风控考量，系统给了市价单较高的购买力系数。在所有订单参数都相同的情况下，选择市价单会比限价单占用更多的购买力。  
- 而且对于不同的品种，和不同的市场情况，风控系统会对市价单的购买力系数做动态调整。所以在下市价单时，若您通过最大购买力去计算最大可买数量，计算的结果很可能是不准确的。  
### 如何计算正确的可买数量  
不建议自己计算，您可以通过 [查询最大可买可卖](../trade/get-max-trd-qtys.html) 接口获取正确的可买数量。  
### 如何尽可能买更多  
您可以用价格为对价的限价单，替代市价单进行交易。  
其中，对价：买1价（下卖单时）或 卖1价（下买单时）  


## Q16：API模拟交易下单，支持美股融资融券模拟账户接入
A：  
API模拟交易下单，已经支持美股融资融券模拟账户接入，交易能力更全面。  
原API接口后续将陆续下线美股模拟交易服务，为保障更优质的使用体验，建议您尽快切换至新接口，畅享专业的美股模拟交易服务。


## Q17：交易接口参数使用说明
### 1. 什么是交易对象？
您的平台账号下一般会开设一个保证金综合账户，其中有多个交易子账户（正常有两个，一个综合证券账户，一个综合期货账户；根据需要还可能有综合外汇账户等其他子账户）。一些特殊用户或机构客户可能会在多个券商下开设多个综合账户。  
创建交易对象，是初步筛选子账户的过程。
- 使用 OpenSecTradeContext 创建的交易对象，调用 get_acc_list 时只会返回**证券交易账户**
- 使用 OpenFutureTradeContext 创建的交易对象，调用 get_acc_list 时只会返回**期货交易账户**  

参数 security_firm 用来筛选对应归属券商的账户，参数 filter_trdmarket  用来筛选对应交易市场权限的账户。
#### 1.1 security_firm 券商参数
Futu API 目前支持的券商有 [这些](../trade/trade.html#572)。  
创建的交易对象，在调用 get_acc_list 时，会返回 security_firm 对应券商的真实账户和所有模拟交易账户（这是因为模拟交易没有券商的概念，所以无论 security_firm 传什么，都会返回所有的模拟账户）。  
security_firm 的默认值是 FUTUSECURITIES，FUTU HK 券商账户可以不填此参数，但需要获取其他券商的账户时，需要修改券商参数。  
* **Example 1**

```python
trd_ctx = OpenSecTradeContext(security_firm=SecurityFirm.FUTUSECURITIES)
ret, data = trd_ctx.get_acc_list()
print(data)
```

* **Output**

```python
               acc_id   trd_env acc_type      uni_card_num          card_num   security_firm sim_acc_type                  trdmarket_auth acc_status
0  281756478396547854      REAL   MARGIN  1001200163530138  1001369091153722  FUTUSECURITIES          N/A  [HK, US, HKCC, HKFUND, USFUND]     ACTIVE
1             3450309  SIMULATE     CASH               N/A               N/A             N/A        STOCK                            [HK]     ACTIVE
2             3548731  SIMULATE   MARGIN               N/A               N/A             N/A       OPTION                            [HK]     ACTIVE
3  281756455998014447      REAL   MARGIN               N/A  1001100320482767  FUTUSECURITIES          N/A                            [HK]   DISABLED
```

* **Example 2**
```python
trd_ctx = OpenSecTradeContext(security_firm=SecurityFirm.FUTUSG)
ret, data = trd_ctx.get_acc_list()
print(data)
```
* **Output**
```python
    acc_id   trd_env acc_type uni_card_num card_num security_firm sim_acc_type trdmarket_auth acc_status
0  3450309  SIMULATE     CASH          N/A      N/A           N/A        STOCK           [HK]     ACTIVE
1  3548731  SIMULATE   MARGIN          N/A      N/A           N/A       OPTION           [HK]     ACTIVE
```


#### 1.2 filter_trdmarket 交易市场参数
Futu API 目前支持的交易市场有 [这些](../trade/trade.html#719)。

创建的交易对象，在调用 get_acc_list 时，会返回所有拥有 filter_trdmarket 市场交易权限的账户；当 filter_trdmarket 入参传 NONE 时，不过滤市场，返回所有的账户。  
filter_trdmarket 的默认参数是 HK，在综合账户体系下，这个参数用来筛选不同市场下的模拟交易账户。  
* **Example 1**

```python
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.US)
ret, data = trd_ctx.get_acc_list()
print(data)
```
* **Output**
```python
               acc_id   trd_env acc_type      uni_card_num          card_num   security_firm sim_acc_type                  trdmarket_auth acc_status
0  281756478396547854      REAL   MARGIN  1001200163530138  1001369091153722  FUTUSECURITIES          N/A  [HK, US, HKCC, HKFUND, USFUND]     ACTIVE
1             3450310  SIMULATE   MARGIN               N/A               N/A             N/A        STOCK                            [US]     ACTIVE
2             3548732  SIMULATE   MARGIN               N/A               N/A             N/A       OPTION                            [US]     ACTIVE
3  281756460292981743      REAL   MARGIN               N/A  1001100520714263  FUTUSECURITIES          N/A                            [US]   DISABLED
```

* **Example 2**
```python
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.NONE)
ret, data = trd_ctx.get_acc_list()
print(data)
```
* **Output**
```python
                acc_id   trd_env acc_type      uni_card_num          card_num   security_firm sim_acc_type                  trdmarket_auth acc_status
0   281756478396547854      REAL   MARGIN  1001200163530138  1001369091153722  FUTUSECURITIES          N/A  [HK, US, HKCC, HKFUND, USFUND]     ACTIVE
1              3450309  SIMULATE     CASH               N/A               N/A             N/A        STOCK                            [HK]     ACTIVE
2              3450310  SIMULATE   MARGIN               N/A               N/A             N/A        STOCK                            [US]     ACTIVE
3              3450311  SIMULATE     CASH               N/A               N/A             N/A        STOCK                            [CN]     ACTIVE
4              3548732  SIMULATE   MARGIN               N/A               N/A             N/A       OPTION                            [US]     ACTIVE
5              3548731  SIMULATE   MARGIN               N/A               N/A             N/A       OPTION                            [HK]     ACTIVE
6   281756455998014447      REAL   MARGIN               N/A  1001100320482767  FUTUSECURITIES          N/A                            [HK]   DISABLED
7   281756460292981743      REAL   MARGIN               N/A  1001100520714263  FUTUSECURITIES          N/A                            [US]   DISABLED
8   281756468882916335      REAL   MARGIN               N/A  1001100610464507  FUTUSECURITIES          N/A                          [HKCC]   DISABLED
9   281756507537621999      REAL     CASH               N/A  1001100910390035  FUTUSECURITIES          N/A                        [HKFUND]   DISABLED
10  281756550487294959      REAL     CASH               N/A  1001101010406844  FUTUSECURITIES          N/A                        [USFUND]   DISABLED
```
::: tip 提示  
当 filter_trdmarket 入参NONE时，可以返回所有的交易账户。其中第0行是真实账户，1~5行均为模拟交易账户，6~10行是已失效的真实账户。这些失效账户都是单市场账户，现已被综合账户替代。但历史订单和历史成交还在这些已失效的账户中，可以通过这些账户来查询。  
OpenFutureTradeContext 对象中没有 filter_trdmarket 参数，只有 security_firm 参数，功能与 OpenSecTradeContext  一样。  
:::  

### 2. 交易接口参数
在使用具体的交易接口（如下单、查询订单列表）时，接口中的 `trd_env`, `acc_index` 和 `acc_id` 参数，会先筛选确认一个唯一的账户，对此账户实施对应的接口行为。
![acc-select](../img/acc-select.jpg)

::: tip 总结
1. 根据 trd_env 筛选出真实账户还是模拟账户
2. 在筛选结果中，优先选择 acc_id 指定的账户
3. 如果 acc_id 为0，则通过 acc_index选取对应账号
4. 报错场景：指定的 acc_id 不存在，或 acc_index 超出范围  
:::


### 3. 应用举例
#### 3.1 综合证券账户实盘下单
```python
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.NONE, security_firm=SecurityFirm.FUTUSECURITIES)
ret, data = trd_ctx.unlock_trade("123123")
if ret == RET_OK:
    print("解锁成功")
    ret, data = trd_ctx.place_order(45, 200, 'HK.00700', TrdSide.BUY,
                                    order_type=OrderType.NORMAL,
                                    trd_env=TrdEnv.REAL,  # 和默认参数一样，可以不填
                                    acc_id=0)  # 和默认参数一样，可以不填
    print(data)
```

#### 3.2 综合期货账户查询实盘订单列表
```python
trd_ctx = OpenFutureTradeContext(security_firm=SecurityFirm.FUTUSECURITIES)

ret, data = trd_ctx.order_list_query(trd_env=TrdEnv.REAL,   # 和默认参数一样，可以不填
                                     acc_id=0)  # 和默认参数一样，可以不填
print(data)
```

#### 3.3 港股模拟现金账户查询账户资金
```python
# filter_trdmarket 填 TrdMarket.HK
# trd_env 填 TrdEnv.SIMULATE
# acc_index 填 0
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK)
ret, data = trd_ctx.accinfo_query(trd_env=TrdEnv.SIMULATE, acc_index=0)
print(data)
```

#### 3.4 美股模拟保证金账户下单期权
```python
# 通过 filter_trdmarket 和 trd_env 筛选完之后只剩两个账户
# 第0个是美股现金账户（交易股票）,第1个是美股保证金账户（交易期权）
# acc_index 填 1 指定美股保证金账户
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.US)
ret, data = trd_ctx.place_order(10, 1, code="US.AAPL250618P550000",trd_side=TrdSide.BUY,
                                trd_env=TrdEnv.SIMULATE,
                                acc_index=1)
print(data)
```

#### 3.5 日本期货模拟账户查询最大可买卖
```python
# 将 get_acc_list 的结果打印出来，可以看到日本期货模拟账户的 acc_id 是 6271199
# 请求最大可买卖接口时传入这个 acc_id 
trd_ctx = OpenFutureTradeContext()
ret, data = trd_ctx.acctradinginfo_query(order_type=OrderType.NORMAL,
                                         price=5000,
                                         trd_env=TrdEnv.SIMULATE,
                                         acc_id=6271199,
                                         code="JP.NK225main")
print(data)
```


### 4. API 中的账户如何与 APP/桌面端对应

![card-app](../img/card-app.png)
APP 上的账户仅显示卡号后 4 位数字，我们将 [get_acc_list](../trade/get-acc-list.html) 的返回结果打印出来后，有 uni_card_num 列和 card_num 列，分别对应综合账户的卡号，和单币种账户（已废弃）的卡号。通过卡号后 4 位数就能把 API 中获取到的账号与 APP 上对应起来了。

---

# 其他

## Q1：如何编译C++ API？

A: 
futu api c++ SDK支持Windows/MacOS/Linux，每个系统提供了以下编译环境生成的库文件：
操作系统|编译工具
:-|:-
Windows |Visual Studio 2013
Centos 7|g++ 4.8.5
Ubuntu 16.04|g++ 5.4.0
MacOS | XCode 11

如果编译器版本不同，或依赖的protobuf版本不同，则可能需要自己使用源码重新编译FTAPI和protobuf，源码位置见下图目录：

```
FTAPI目录结构：
+---Bin                               存放各个系统默认编译环境编译出的依赖库
+---Include                           存放公共头文件，以及proto协议生成的.h/.cc文件
+---Sample                            示例工程
\---Src
    +---FTAPI                         FTAPI源码
    +---protobuf-all-3.5.1.tar.gz     protobuf源码
```

#### 编译步骤：
1. 重新编译protobuf：生成libprotobuf静态库
2. 从协议proto文件中生成C++文件
3. 重新编译FTAPI: 源码在Src/FTAPI，生成libFTAPI静态库

#### 步骤1： 重新编译protobuf：
- Windows：
  - 安装CMake
  - 打开VS命令行工具，cd到protobuf/cmake目录
  - 执行：cmake -G "Visual Studio 12 2019" -DCMAKE_INSTALL_PREFIX=install -Dprotobuf_BUILD_TESTS=OFF  这样会生成Visual Studio 2019的项目文件，其它版本Visual Studio请修改-G参数
  - 打开生成的Visual Studio项目文件，平台工具集设置为v120_xp，编译即可
- Linux（参考protobuf/src/README）
  - 执行 ./autogen.sh
  - 执行 CXXFLAGS="-std=gnu++11" ./configure --disable-shared
  - 执行 make
  - 将生成的libprotobuf.a放入Bin/Linux目录
- MacOS（参考protobuf/src/README）
  - 使用brew安装这些依赖库：autoconf automake libtool
  - 执行./configure CC=clang CXX="clang++ -std=gnu++11 -stdlib=libc++" --disable-shared

#### 步骤2: 重新生成proto代码
- 上面编译Protobuf后会同时生成可执行文件protoc。用protoc将Include/Proto下面的.proto文件生成对应的.h和.cc文件。例如命令以下命令会从Common.proto生成对应的Common.pb.h和Common.pb.cc
  - protoc -I="FTAPI路径/Include/Proto" --cpp_out="." FTAPI路径/Include/Proto/Common.proto
- 将生成的.h和.cc文件放到Include/Proto下面

#### 步骤3: 重新编译FTAPI
- Windows：新建Visual Studio C++静态库工程，将Src/FTAPI和Include下的源码加入工程中，平台工具集设置为v120_xp，然后编译
- Mac：新建XCode C++静态库工程，将Src/FTAPI和Include下的源码加入工程中，然后编译
- Linux：使用CMake编译FTAPI静态库，在FTAPI路径/Src目录下执行：
  - cmake -DTARGET_OS=Linux

## Q2：有没有更完整的策略样例可以参考？

A:
* Python 策略样例在 /futu/examples/ 文件夹下。您可以通过执行如下命令，找到 Python API 的安装路径：
    ```
    import futu
    print(futu.__file__)
    ```
* C# 策略样例在 /FTAPI4NET/Sample/ 文件夹下
* Java 策略样例在 /FTAPI4J/sample/ 文件夹下
* C++ 策略样例在 /FTAPI4CPP/Sample/ 文件夹下
* JavaScript 策略样例在 /FTAPI4JS/sample/ 文件夹下


## Q3：使用 python API 导入异常

A：

**场景一**：已经在 Python 环境中安装了 futu 模块，仍然提示 No module named 'futu'？  
很可能是因为当前 IDE 所使用的 interpreter 并不是你装过 futu 模块的 interpreter。也就是说，您的电脑可能装了两个以上的 Python 环境。
您可以操作如下两步：
1. 在 Python 中运行如下代码，得到当前 interpreter 的路径：
```
import sys
print(sys.executable)
```
示例图：  
 ![No module named 'futu'](../img/import-futu-error.png)

2. 在命令行中，执行 `$ D:\software\anaconda3\python.exe -m pip install futu-api`（其中前半部分的文件路径来自第 1 步打印的路径）。
这样就可以在当前的 interpreter 中也安装一份 futu 模块。

## Q4： import 成功了，仍然调用不了相关接口？ 

A：通常遇到这种情况，需要确认一下：成功导入的 futu，是不是真正的 Futu API 模块。以下几种场景也可能 import 成功。

**场景一**：存在与“futu”重名的文件

  1. 当前文件名是 futu.py
  2. 当前文件所在目录下存在另一个名为 futu.py 的文件
  3. 当前文件所在目录下存在名为 `/futu` 的文件夹    

因此，我们强烈建议您，在给文件 / 文件夹 / 工程起名的时候，不要起名叫“futu”。重名一时爽，查 bug 两行泪。

**场景二**：误装了一个名为“futu”的第三方库  

   Futu API 的正确名称为`futu-api`，而非“futu”。   

   如果您安装过名为“futu”的第三方库，请将其卸载，并 [下载 futu-api](../quick/demo.md#4688)。
   
   以 PyCharm 为例：查看第三方库的安装情况。

   ![settings](../img/settings.png)  
   ![futuku](../img/futuku.png)


## Q5：协议加密相关

A：  
### 概述
您可以使用非对称加密算法 RSA，对策略程序（Futu API）与 OpenD 之间的请求和返回内容进行加密，以保证通信安全。  
如果您的策略程序（Futu API）与 FutuOpenD 在同一台电脑上，则通常无需加密。

### 协议加密流程
您可以尝试通过以下步骤解决此问题：
1. 通过第三方 web 平台自动生成密钥文件。  
    - 具体方法：在 baidu 或 google 上搜索“RSA 在线生成”，**密钥格式**设置为 PKCS#1，**密钥长度**设置为 1024 bit，不需要设置私钥密码，点击**生成密钥对**。  
    ![ui-config](../img/create_rsa.png)  

2. 将生成的 **RSA 加密私钥** 复制粘贴至 txt 记事本，并保存至 OpenD 所在电脑的指定路径。
3. 在 OpenD 所在的电脑中，指定 **RSA 加密私钥** 的路径。  
    - 方式一：在 [可视化 OpenD](../quick/opend-base.md#4147) 启动界面右侧的“加密私钥”一栏，指定上一步骤中放置 **RSA 加密私钥** 的路径。如下图所示：  
    ![ui-config](../img/nnrsa_ui-config.png)  
    - 方式二：在 [命令行 OpenD](../opend/opend-cmd.md#8799) 启动文件 OpenD.xml 中，找到参数`rsa_private_key`，将其配置为第 2 步中 **RSA 加密私钥** 的路径。如下图所示：  
    ![ui-config](../img/nnrsa_xml.png)  
4. 将第 2 步中 txt 文件另存至策略程序（Futu API）所在电脑的指定路径， 并在策略程序中将此路径 [设置为私钥路径](../ftapi/init.md#5641)。
5. 在策略程序（Futu API）中启用协议加密。 启用协议加密的方式有两种，其中方式二的优先级更高。
    - 方式一：对单条的连接加密（通用）。在对 [行情对象](../quote/base.md#7902) 或 [交易对象](../trade/base.md#7902) 创建连接时，通过 **是否启用加密** 参数设置加密。
    - 方式二：对所有的连接加密（仅 Python）。通过`enable_proto_encrypt`接口设置加密，详见 [这里](../ftapi/init.md#319)。


:::tip 提示
* 在 OpenD 或策略程序（Futu API）中指定 **RSA 加密私钥** 路径时，需指定至 txt 文件本身。
* RSA 加密公钥无需保存，可通过私钥计算得到。
:::


## Q6：为什么我获取的 DataFrame 数据，只能展示一部分 ？

A：打印 pandas.DataFrame 数据的时候，如果行列数过多，pandas 默认会将数据折叠，导致看起来显示不全。  
因此，并不是接口返回数据真的不全。您只需要在 Python 脚本前面加上如下代码即可解决。

```
import pandas as pd
pd.options.display.max_rows=5000
pd.options.display.max_columns=5000
pd.options.display.width=1000
```

## Q7：Mac 机器使用 C++ 语言的 API，遇到 “无法打开 libFTAPIChannel.dylib” 的问题

A：在对应库目录中执行以下命令即可解决:`$ xattr -r -d com.apple.quarantine libFTAPIChannel.dylib`。


## Q8：Python 用户，为什么在 OpenD 配置文件中设置了日志级别为 no 后，log 文件夹下仍然持续产生超大容量的日志文件？

A：OpenD 配置文件中的日志级别参数，只用来控制 OpenD 产生的日志。而 Python API 默认也会产生日志，如果您不希望希望 Python API 产生日志，可以在 Python 脚本加上如下语句：

```
logger.file_level = logging.FATAL  # 用于关闭 Python API 日志
logger.console_level = logging.FATAL  # 用于关闭 Python 运行时的控制台日志
```


## Q9：对于 5.4 及以上的版本，Java API 的库名和配置方式的变更

A:
* 如果您是 Java API 5.3 及以下版本的用户，在更新版本时，请注意以下变更：

  **配置流程的变更**：

  1. 通过 [富途牛牛官网](https://www.futunn.com/download/OpenAPI)下载 Futu API。
  2. 解压下载好的 FTAPI 文件，`/FTAPI4J` 是 Java API 的目录，将目录结构中的 `/lib/futu-api-.x.y.z.jar` 添加到您的工程设置中。创建 futu-api 工程请参考 [这里](../quick/demo.html#2927)。


  **目录结构的变更**：
  1. Futu API 的 Java 版本，库名由之前的 ftapi4j.jar 变更为 `futu-api-x.y.z.jar`，其中 “x.y.z” 表示版本号。
  2. 第三方库的引用中，去掉了 /lib/jna.jar 和 /lib/jna-platform.jar 依赖，增加了 `/lib/bcprov-jdk15on-1.68.jar` 和 `/lib/bcpkix-jdk15on-1.68.jar` 依赖。
    ```
    +---ftapi4j                      futu-api 源码，如果所用 JDK 版本不兼容可以用这里的工程重新编译出 futu-api.jar
    +---lib                          存放公共库文件
    |    futu-api-x.y.z.jar          Futu API 的 Java 版本
    |    bcprov-jdk15on-1.68.jar     第三方库，用于加解密
    |    bcpkix-jdk15on-1.68.jar     第三方库，用于加解密
    |    protobuf-java-3.5.1.jar     第三方库，用于解析 protobuf 数据
    +---sample                       示例工程
    +---resources                    maven 工程默认生成的目录
    ```
* 如果您第一次接触 Futu API，我们提供了更便捷的通过 maven 仓库配置 Java API 的方式。配置流程请参考 [这里](../quick/demo.html#5757)。


## Q10：Python 用户，使用 pyinstaller 打包脚本时报错：找不到 Common_pb2 模块

A：你可以尝试通过以下步骤解决此问题：
1. 假设你需要对 main.py 进行打包。使用命令行语句，运行代码：pyinstaller main.py，不要加参数 “- F”（path 为 main.py 的所在路径）
  ```
  pyinstaller path\main.py
  ```
  打包成功后，main.py 所在目录下的 /dist 中，会生成 /main 文件夹，main.exe 就在这个文件夹中。  
  ![dist](../img/dist.png)  
2. 运行以下代码，找到 futu-api 的安装目录。  
  ```
  import futu
  print(futu.__file__)
  ```
  运行结果:  
  ```
  C:\Users\ceciliali\Anaconda3\lib\site-packages\futu\__init__.py
  ```
  ![path_futu](../img/path_futu.png)  

3. 打开上图文件夹中的 /common/pb，将所有文件全部复制到 /main 中。

4. 在 /main 中创建文件夹，命名为 futu，将上图文件夹中的 `VERSION.txt` 文件复制到 /main/futu 中。  
  ![main_futu](../img/main_futu.png) 
5. 再次尝试运行 main.exe

## Q11：接口调用结果正常，但其返回表现不符合预期？
A:
* 接口调用结果正常，表示富途已经成功收到并响应了您的请求，但接口返回表现可能与您的预期不符。  

  例如：若您在非交易时段调用 [订阅](../quote/sub.md) 接口，虽然您的请求可以被成功响应，并且接口调用结果正常，但在非交易时段下，交易所无行情数据变动，所以您将暂时无法收到行情数据推送，直至市场重新回到交易时段。  
* 接口调用结果可以通过返回字段（定义参见：[接口调用结果](../ftapi/common.md#7467)）查看，返回字段为 0 代表接口调用正常，非 0 代表接口调用失败。  
  
  对于 Python 用户，下面两种写法等价：
  ```
  if ret_code == RET_OK:
  ```
  ```
  if ret_code == 0:
  ```

## Q12：WebSocket相关
A：

### 概述

Futu API 中，WebSocket 主要用于以下两方面：
* 可视化 OpenD 中，UI 界面跟底层的命令行 OpenD 的通信使用 WebSocket 方式。
* JavaScript API 跟 OpenD 之间的通信使用 WebSocket 方式。

![WebSocket-struct](../img/WebSocket-struct.png)  
* 当 WebSocket 启动时，命令行 OpenD 会与 **FTWebSocket 中转服务** 建立 Socket 连接（TCP），这一连接会用到默认的 **监听地址** 和 **API 协议监听端口**。
* 同时，JavaScript API 会与 **FTWebSocket 中转服务** 建立 WebSocket 连接（HTTP），这一连接会用到 **WebSocket 监听地址** 和 **WebSocket 端口**。

### 使用
为保证账户安全，当 WebSocket 监听来自非本地请求时，我们强烈建议您启用 SSL 并配置 **WebSocket 鉴权密钥**。

SSL 通过在配置 **WebSocket 证书** 以及 **WebSocket 私钥** 来启用。  
命令行 OpenD 可通过配置 OpenD.xml 或配置命令行参数来设置文件路径。可视化 OpenD 点击【更多选项】下拉菜单，可以看到设置项。

![ui-more-config](../img/ui-more-config.png)

::: tip 提示
如果证书是自签的，则需要在调用 JavaScript 接口所在机器上安装该证书，或者设置不验证证书。
:::

#### 生成自签证书
自签证书生成详细资料不便在此文档展开，请自行查阅。  
在此提供较简单可用的生成步骤：
1. 安装 openssl。
2. 修改 openssl.cnf，在 alt_names 节点下加上 OpenD 所在机器 IP 地址或域名。  
例如：IP.2 = xxx.xxx.xxx.xxx, DNS.2 = www.xxx.com
3. 生成私钥以及证书（PEM）。

**证书生成参数参考如下**：  
`openssl req -x509 -newkey rsa:2048 -out futu.cer -outform PEM -keyout futu.key -days 10000 -verbose -config openssl.cnf -nodes -sha256 -subj "/CN=Futu CA" -reqexts v3_req -extensions v3_req`

::: tip 提示
* openssl.cnf 需要放到系统路径下，或在生成参数中指定绝对路径。
* 注意生成私钥需要指定不设置密码（-nodes）。
:::

附上本地自签证书以及生成证书的配置文件供测试：  
* [openssl.cnf](../file/openssl.cnf)  
* [futu.cer](../file/cer)  
* [futu.key](../file/key)

## Q13：API 的行情和交易服务分别部署在哪里？
A：  
- 行情：  

平台账号|行情服务器所在地
:-|:-|:-
牛牛号|腾讯云广州和香港
moomoo 号|腾讯云美国弗吉尼亚和新加坡

- 交易：  

所属券商|交易服务器所在地
:-|:-|:-
富途证券(香港)|香港
moomoo证券(美国)|腾讯云美国弗吉尼亚
moomoo证券(新加坡) |腾讯云新加坡
moomoo证券(澳大利亚)|腾讯云新加坡
moomoo证券(马来西亚)|阿里云马来西亚
moomoo证券(加拿大)|AWS加拿大
moomoo证券(日本)|腾讯云日本


## Q14：关于综合账户升级的过渡指引

### 1. [**综合账户升级**](https://www.futuhk.com/hans/support/topic2_1734)
综合账户支持以多种货币在同一个账户内交易不同市场品类。从单币种账户升级到综合账户，是在您原来的牛牛号下，进行账户迁移。主要包括：
- 创建新的综合账户
- 将您原来单币种业务账户里的资产，转移到综合账户里
- 关闭原来的单币种账户

### 2. **OpenD版本升级**
我们会在 2024年9月14日、15日 集中为 Futu API 客户的账户做升级，请提前检查 OpenD 和 API 版本号：  
- **7.01 及以下版本**  
  OpenD 因版本过旧，将于 2024/09/14 停止服务。届时，已登录的账户会被强制退出登录。我们建议您在 9/14 之前升级 [OpenD](../quick/opend-base.html#4147) 和 [API](../quick/demo.html#4688) 至最新版本，且不要在 9/14~9/15 期间跨周末运行策略。
- **7.02 ~ 8.2 版本**  
  OpenD 版本较旧，无法获取综合账户。我们建议您在 9/14 之前升级 [OpenD](../quick/opend-base.html#4147) 和 [API](../quick/demo.html#4688) 至最新版本，且不要在 9/14~9/15 期间跨周末运行策略。
- **8.3 及以上版本**  
  可以正常使用，我们建议您不要在 9/14~9/15 期间跨周末运行策略。  

综合账户升级时，您的资产会转移到新的综合账户，如果策略指定旧的账户，可能会运行异常。同时，在实盘交易之前，建议您进行必要的检查与测试，确保一切设置正常。

### 3. **账户升级后，Futu API有哪些表现？**
- Python API 将不再支持使用 OpenHKTradeContext,  OpenUSTradeContext, OpenHKCCTradeContext, OpenCNTradeContext 创建交易对象，请参考 [创建交易对象连接](../trade/base.html#7902) 改用 OpenSecTradeContext。  
- 非Python API用户，在使用 Trd_GetAccList 接口时，需要将 needGeneralSecAccount 参数设为 true，才能获取到综合账户的相关信息。  
- 账户新增 [账户状态](../trade/trade.html#121): 在使用 [获取交易业务账户列表](../trade/get-acc-list.html#5754) 时，返回结果新增了账户状态 。综合账户标记为 `ACTIVE` 生效账户，被停用的单币种账户标记为 `DISABLED` 失效账户。  
- [下单](../trade/place-order.html#4080)、[改单撤单](../trade/modify-order.html#7408)、[查询最大可买可卖](../trade/get-max-trd-qtys.html#2713) 等交易接口表现  
    - 支持使用 `ACTIVE` 生效账户所对应的 acc_id或acc_index 进行购买力查询与交易。
    - 不支持使用 `DISABLED` 失效账户所对应的 acc_id或acc_index 进行购买力查询与交易，若使用，将会出现报错信息。
    - Python API用户：在接口入参中，请指定 acc_id 为升级后的综合账户。
    - 非Python API用户：在 TrdHeader 中，请指定accID为升级后的综合账户。

---

# 更新日志

## 2026-06-25

### [OpenD 10.8.6808](https://www.futunn.com/download/OpenAPI)


* 支持[行情搜索](../quote/get-search-quote.md)接口，关键词智能搜索行情标的，一键定位目标资产   
* 支持[资讯搜索](../quote/get-search-news.md)接口，关键词搜资讯，新闻、公告、评级一网打尽   
* [指标列表](../quote/get-indicator-list.md)全量开放，支持麦语言、Python，技术分析触手可及  
* 期权数据全维覆盖：IV/HV、Put/Call 比、末日期权、财报期权、卖方策略，期权玩家必备，详见[行情接口](../quote/overview.md)   
* 市场基本面数据上线：机构追踪、精选宏观数据、派息/财报日历、各类榜单、产业链、FedWatch，洞察先机，详见[行情接口](../quote/overview.md)


## 2026-06-04

### [OpenD 10.7.6708](https://www.futunn.com/download/OpenAPI)


* 支持获取新加坡股票、马来西亚股票、日本股票行情数据，支持实时报价、摆盘、K线、基本面数据等多种能力，权限详见 [行情权限](../intro/authority.md#2867)   
* 支持交易新加坡股票、马来西亚股票、日本股票，订单能力全面对齐 App 端，覆盖 HK/SG/MY/JP 地区用户   
* 支持组合期权行情与交易能力，覆盖跨式、价差、蝶式等多种策略。支持[获取期权策略](../quote/get-option-strategy.md)、[期权损益分析](../quote/get-option-strategy-analysis.md)、[期权快照](../quote/get-option-quote.md) 等行情数据，通过[组合下单](../trade/place-combo-order.md) 交易组合期权，[查询组合期权购买力](../trade/comboorder-tradinginfo-query.md) 变动信息


## 2026-05-21

### [OpenD 10.6.6608](https://www.futunn.com/download/OpenAPI)


* 像在客户端一样组合筛选条件：通过 API 直接调用 [筛选正股](../quote/get-stock-screen.md#3910) 接口，从基本面、技术面、形态面 5 大维度自由组合，一行代码筛出符合策略的股票  
* 像在客户端一样查询个股基本面数据：通过 API 直接调用 [个股基本面数据](../quote/get-financials-statements.md#6376) 接口获取财务三大表、主营构成、分析师评级、晨星研报、估值（PE/PB/PS）、分红回购拆股、股东持股、内部人交易、公司概况与高管、十大经纪商、卖空数据


## 2026-05-07

### [OpenD 10.5.6508](https://www.futunn.com/download/OpenAPI)

* 新增加密货币（Crypto）行情与交易支持，覆盖 HK/US/SG 地区用户
* 新增加密货币账户资金、持仓、订单记录、资金流水查询
* K线类型 [KLType](../quote/quote.md#4119) 新增 `K_10M`(10分K)、`K_120M`(2小时K)、`K_180M`(3小时K)、`K_240M`(4小时K)
* OpenD Skills 支持加密货币功能


## 2026-04-23

### [OpenD 10.4.6408](https://www.futunn.com/download/OpenAPI)

* 交易对象连接 `OpenSecTradeContext()`, `OpenFutureTradeContext()`, `OpenCryptoTradeContext()` `security_firm` 参数默认值变更为 `NONE`，系统将自动匹配当前账户所属券商，无需手动指定
* 新增日志静默模式，支持关闭 OpenD 日志输出
* Windows 安装包文件名嵌入版本号，便于版本识别与管理
* OpenD Skills 性能优化


## 2026-04-16

### [OpenD 10.3.6308](https://www.futunn.com/download/OpenAPI)

* 美股实时行情推广期免费开放
* OpenD 支持未开户用户登录使用，附赠 100 只标的实时行情订阅额度及历史 K 线请求额度
* 历史 K 线请求额度重置周期由 30 天缩短至 7 天


## 2026-03-26

### [OpenD 10.2.6208](https://www.futunn.com/download/OpenAPI)

* API 新增美股融资融券模拟交易支持，通过设置 `TrdEnv.SIMULATE` 即可进行模拟下单，订单状态实时同步至 App 端
* OpenD Skills 性能优化


## 2026-03-20

### OpenD 10.1.6108

* 全新推出 [Futu Skills Hub](https://www.futunn.com/skillhub)，支持 OpenClaw、Claude Code、Cursor、Codex 等主流 AI Agent 接入
* 行情与交易 [Futu API Skill](https://www.futunn.com/skillhub/openapi) 覆盖 56 个 API 接口，支持香港、美国、沪深、新加坡、日本等市场，覆盖实时行情、智能交易、实时推送三大能力


## 2026-03-06

### OpenD 10.0.6018

* 修复近期已知问题


## 2025-12-17

### OpenD 9.6.5608

* 行情接口新增恒生系列指数支持，涵盖 HK.800733、HK.800734 等 82 个指数标的
* [获取交易账户列表](../trade/get-acc-list.md#5754)接口 `TrdAccRole()` 新增支持获取机构主账户，`TrdAccRole.MASTER` 表示主账户（主账户不支持交易操作）
* 修复近期已知问题


## 2025-08-14

### OpenD 9.4.5408

* 支持美股全时段订单，下单接口 [place_order()](../trade/place-order.md)传入 `Session.ALL` 即可覆盖盘前、盘中及盘后时段
* 历史日 K 数据范围扩展至近 20 年
* 美国股票 LV2 深度摆盘升级至 60 档聚合盘口数据；美国期货 LV2 升级至 40 档盘口数据
* 新增公司分立（Spin-off）行动的复权数据支持
* [获取期货合约资料](../quote/get-future-info.md)接口中 `min_change_unit`（最小变动单位）字段已废弃