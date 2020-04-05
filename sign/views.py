from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from sign.models import Event, Guest
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# 登陆动作
@login_required
def login_action(request):
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            # return HttpResponse("login success!")
            response = HttpResponsePermanentRedirect("/event_manage/")
            # 添加浏览器cookies
            # response.set_cookie("user", username, 3600)
            # 将session信息记录到服务器
            request.session['user'] = username
            return response
        else:
            return render(request, "index.html", {"error": "username or password error!"})


# 退出登陆
@login_required
def logout(request):
    auth.logout(request)
    response = HttpResponsePermanentRedirect("/index/")
    return response


def index(request):
    # return HttpResponse("hello django!")
    return render(request, "index.html")


# 发布会管理
@login_required
def event_manage(request):
    # 读取浏览器session
    username = request.session.get("user", "")
    event_list = Event.objects.all()
    return render(request, "event_manage.html", {"user": username,
                                                 "events": event_list, })


# 嘉宾管理
@login_required
def guest_manage(request):
    # 读取浏览器session
    username = request.session.get('user', '')
    # 从guest表获取到的数据需要排序，这里根据id字段升序排序。如果不排序，会提示：
    # UnorderedObjectListWarning: Pagination may yield inconsistent results with an unordered object_list:
    # <class 'sign.models.Guest'> QuerySet.
    guest_list = Guest.objects.all().order_by("id")
    # 把查询出来的所有嘉宾（列表guest_list）放到Paginator类中，划分为每页显示2条数据
    paginator = Paginator(guest_list, 2)
    page = request.GET.get("page")
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # 如果page不是整数，取第一页的数据
        contacts = paginator.page(1)
    except EmptyPage:
        # 如果page不在范围，取最后一页
        contacts = paginator.page(paginator.num_pages)
    return render(request, "guest_manage.html", {"user": username,
                                                 "guests": contacts, })


# 发布会查询管理
@login_required
def search_event_name(request):
    username = request.session.get("user", "")
    search_name_event = request.GET.get("name", "")
    event_list = Event.objects.filter(name__contains=search_name_event)
    return render(request, "event_manage.html", {"user": username,
                                                 "events": event_list, })


# 嘉宾查询管理
@login_required
def search_guest_name(request):
    # username = request.session.get("user", "")
    # search_name_guest = request.GET.get("realname", "")
    # guest_list = Guest.objects.filter(realname__contains=search_name_guest)
    # return render(request, "guest_manage.html", {"user": username,
    #                                              "guests": guest_list, })
    username = request.session.get("user", "")
    search_name_guest = request.GET.get("realname", "")
    # 通过realname字段检索获取到的数据也需要排序，这里根据id字段升序排序。如果不排序，会提示：
    # UnorderedObjectListWarning: Pagination may yield inconsistent results with an unordered object_list:
    # <class 'sign.models.Guest'> QuerySet.
    guest_list = Guest.objects.filter(realname__contains=search_name_guest).order_by("id")
    # 把查询出来的所有嘉宾（列表guest_list）放到Paginator类中，划分为每页显示2条数据
    paginator = Paginator(guest_list, 2)
    page = request.GET.get("page")
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # 如果page不是整数，取第一页的数据
        contacts = paginator.page(1)
    except EmptyPage:
        # 如果page不在范围，取最后一页
        contacts = paginator.page(paginator.num_pages)
    return render(request, "guest_manage.html", {"user": username,
                                                 "guests": contacts, })


# 签到页面
@login_required
def sign_index(request, eid):
    event = get_object_or_404(Event, id=eid)
    return render(request, "sign_index.html", {"event": event})


# 签到功能
@login_required
def sign_index_action(request, eid):
    event = get_object_or_404(Event, id=eid)
    phone = request.POST.get("phone", "")
    print(phone)
    result = Guest.objects.filter(phone=phone)
    if not result:
        return render(request, "sign_index.html", {"event": event,
                                                   "hint": "Phone number does not exist", })
    result = Guest.objects.filter(phone=phone, event_id=eid)
    if not result:
        return render(request, "sign_index.html", {"event": event,
                                                   "hint": "There is no corresponding mobile number for this conference", })
    # 到这一步，result返回一个唯一的值，如果不唯一，那么会抛异常：
    # Exception Value: get() returned more than one Guest -- it returned 3!
    # 结合本例，说明返回了3个手机号为查询的手机号，所以才会提示这个错误。解决方法是，保证查询的手机号在数据库是唯一的
    result = Guest.objects.get(phone=phone, event_id=eid)
    if result.sign:
        return render(request, "sign_index.html", {"event": event,
                                                   "hint": "You've signed in", })
    else:
        Guest.objects.filter(phone=phone, event_id=eid).update(sign="1")
        return render(request, "sign_index.html", {"event": event,
                                                   "hint": "Sign in successfully",
                                                   "guest": result, })

