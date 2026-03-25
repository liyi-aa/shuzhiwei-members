import flet as ft
import json
import os
from datetime import datetime

# 数据文件路径
DATA_FILE = "shuzhiwei_members.json"
members = {}

def load_members():
    global members
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                members = json.load(f)
        except:
            members = {}
    else:
        members = {}

def save_members():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(members, f, ensure_ascii=False, indent=2)

def show_msg(page, msg):
    page.snack_bar = ft.SnackBar(
        content=ft.Text(msg),
        duration=2000
    )
    page.snack_bar.open = True
    page.update()

def main(page: ft.Page):
    page.title = "蜀之味麻辣香锅"
    page.padding = 20
    page.window_width = 480
    page.window_height = 850
    page.window_resizable = False
    page.scroll = "always"

    load_members()

    # 组件
    name_input = ft.TextField(label="会员姓名", width=400)
    phone_input = ft.TextField(label="手机号", width=400)
    search_input = ft.TextField(label="查询会员", width=400)
    stats_text = ft.Text("", size=14)
    member_list = ft.ListView(height=400, spacing=10, padding=10, expand=True)

    # 刷新列表
    def refresh_list():
        keyword = search_input.value.strip() if search_input.value else ""
        member_list.controls.clear()
        display = {}
        for p, inf in members.items():
            if keyword == "" or keyword in p or keyword in inf["name"] or (len(keyword)==4 and p.endswith(keyword)):
                display[p] = inf

        if not display:
            member_list.controls.append(ft.Text("暂无会员", size=16))
        else:
            for p, info in display.items():
                card = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(info["name"], size=18, weight=ft.FontWeight.BOLD),
                            ft.Text(f"¥{info['balance']:.2f}", size=16),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(f"手机号：{p}", size=12),
                        ft.Text(f"注册：{info.get('join_date', '')[:10]}", size=11),
                    ]),
                    padding=15,
                    border_radius=10,
                    on_click=lambda e, ph=p: go_detail(ph)
                )
                member_list.controls.append(card)

        total = len(display)
        total_bal = sum(x["balance"] for x in display.values())
        stats_text.value = f"显示：{total}人 | 总余额：¥{total_bal:.2f}"
        page.update()

    # 添加会员
    def add_member(e):
        name = name_input.value.strip()
        phone = phone_input.value.strip()
        if not name:
            show_msg(page, "请填写会员姓名")
            return
        if not phone or len(phone)!=11 or not phone.isdigit():
            show_msg(page, "请输入正确11位手机号")
            return
        if phone in members:
            show_msg(page, "会员已存在")
            return

        members[phone] = {
            "name": name,
            "balance": 0,
            "join_date": datetime.now().strftime("%Y-%m-%d")
        }
        save_members()
        show_msg(page, f"欢迎 {name}")
        name_input.value = ""
        phone_input.value = ""
        refresh_list()

    # 页面切换
    def go_home():
        page.controls.clear()
        render_home()
        page.update()

    def go_detail(phone):
        page.controls.clear()
        render_detail(phone)
        page.update()

    # 首页
    def render_home():
        search_input.on_change = lambda e: refresh_list()
        add_btn = ft.ElevatedButton("添加新会员", width=400, on_click=add_member)

        page.add(
            ft.Column([
                ft.Text("蜀之味麻辣香锅", size=28, weight=ft.FontWeight.BOLD),
                ft.Text("会员管理系统", size=16),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Divider(),
            ft.Text("查询会员", size=18, weight=ft.FontWeight.BOLD),
            search_input,
            ft.Divider(),
            ft.Text("添加会员", size=18, weight=ft.FontWeight.BOLD),
            name_input, phone_input, add_btn,
            ft.Divider(),
            ft.Text("会员列表", size=18, weight=ft.FontWeight.BOLD),
            stats_text,
            member_list
        )
        refresh_list()

    # 详情页
    def render_detail(phone):
        if phone not in members:
            go_home()
            return

        info = members[phone]
        name = info["name"]
        amount_input = ft.TextField(label="金额", value="0", width=200)

        # 充值
        def do_recharge(e):
            try:
                amt = float(amount_input.value)
                if amt <= 0:
                    show_msg(page, "金额必须大于0")
                    return
                members[phone]["balance"] += amt
                save_members()
                show_msg(page, "充值成功")
                go_detail(phone)
            except:
                show_msg(page, "请输入数字")

        # 消费
        def do_consume(e):
            try:
                amt = float(amount_input.value)
                if amt <= 0 or members[phone]["balance"] < amt:
                    show_msg(page, "余额不足或金额错误")
                    return
                members[phone]["balance"] -= amt
                save_members()
                show_msg(page, "消费成功")
                go_detail(phone)
            except:
                show_msg(page, "请输入数字")

        # 删除功能 - 直接删除，无弹窗
        def delete_member(e):
            if phone in members:
                del members[phone]
                save_members()
                show_msg(page, f"{name} 已删除")
                go_home()

        page.add(
            ft.Text("会员详情", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Column([
                    ft.Text(f"姓名：{name}"),
                    ft.Text(f"手机号：{phone}"),
                    ft.Text(f"余额：¥{info['balance']:.2f}"),
                ]),
                padding=20, border_radius=10
            ),
            amount_input,
            ft.Row([ft.ElevatedButton("充值", on_click=do_recharge), ft.ElevatedButton("消费", on_click=do_consume)]),
            ft.Row([ft.ElevatedButton("删除会员", on_click=delete_member), ft.ElevatedButton("返回", on_click=go_home)]),
        )

    go_home()

if __name__ == "__main__":
    ft.app(target=main)