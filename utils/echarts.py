import json
from random import randrange

from django.http import HttpResponse
from pyecharts.charts import Bar, EffectScatter, Scatter, Grid, Pie
from pyecharts.faker import Faker

from pyecharts import options as opts
from jinja2 import Environment, FileSystemLoader
from pyecharts.globals import CurrentConfig

CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("./templates/echarts"))


def response_as_json(data):
    json_str = json.dumps(data)
    response = HttpResponse(
        json_str,
        content_type="application/json",
    )
    response["Access-Control-Allow-Origin"] = "*"
    return response


def json_response(data, code=200):
    data = {
        "code": code,
        "msg": "success",
        "data": data,
    }
    return response_as_json(data)


def json_error(error_string="error", code=500, **kwargs):
    data = {
        "code": code,
        "msg": error_string,
        "data": {}
    }
    data.update(kwargs)
    return response_as_json(data)


JsonResponse = json_response
JsonError = json_error


def base_bar() -> Bar:
    c = (
        Bar()
            .add_xaxis(["leave1", "leave2", "leave3", "leave4"])
            .add_yaxis("商家A", [randrange(0, 100) for _ in range(4)])
            .add_yaxis("商家B", [randrange(0, 100) for _ in range(4)])
            .set_global_opts(title_opts=opts.TitleOpts(title="Bar-基本示例", subtitle="我是副标题"))
        # .dump_options_with_quotes()
    )
    return c


def base_effect_scatter(opts=None) -> EffectScatter:
    c = (
        EffectScatter()
            .add_xaxis(Faker.choose())
            .add_yaxis("", Faker.values())
            .set_global_opts(
            title_opts=opts.TitleOpts(title="疲れ診断結果--分散分析"),
            xaxis_opts=opts.AxisOpts(splitline_opts=opts.SplitLineOpts(is_show=True)),
            yaxis_opts=opts.AxisOpts(splitline_opts=opts.SplitLineOpts(is_show=True)),
        )
            .dump_options_with_quotes()
        # .render("effectscatter_splitline.html")
    )
    return c


def base_scatter(data) -> Scatter:
    x_data = []
    y_data = [[], [], [], []]
    user = []
    pulse = []
    text = ""
    for i in range(len(data)):
        x_data.append(data[i].create_time.strftime("%Y-%m-%d %H:%M:%S"))
        user.append(data[i].user.nickname)

        # text += str(data[i].create_time)+'+'
        if data[i].level == 1:
            y_data[0].append(data[i].pulse)
            y_data[1].append(None)
            y_data[2].append(None)
            y_data[3].append(None)
            text += '1+'
        elif data[i].level == 2:
            y_data[0].append(None)
            y_data[1].append(data[i].pulse)
            y_data[2].append(None)
            y_data[3].append(None)
            text += '2+'
        elif data[i].level == 3:
            y_data[0].append(None)
            y_data[1].append(None)
            y_data[2].append(data[i].pulse)
            y_data[3].append(None)
            text += '3+'
        elif data[i].level == 4:
            y_data[0].append(None)
            y_data[1].append(None)
            y_data[2].append(None)
            y_data[3].append(data[i].pulse)
            text += '4+'

    c = (
        Scatter()
            .add_xaxis(x_data)
            .add_yaxis("leave1", y_data[0])
            .add_yaxis("leave2", y_data[1])
            .add_yaxis("leave3", y_data[2])
            .add_yaxis("leave4", y_data[3])
            .set_global_opts(
            title_opts=opts.TitleOpts(title="疲れ診断結果--分析"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            datazoom_opts=[opts.DataZoomOpts()],
            xaxis_opts=opts.AxisOpts(axislabel_opts={"rotate": 45}),
            # title_opts=opts.TitleOpts(title=text),
            visualmap_opts=opts.VisualMapOpts(type_="size", max_=200, min_=1),
        )
        .dump_options_with_quotes()
    )
    return c
