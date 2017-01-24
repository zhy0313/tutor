#!/usr/bin/env python
# -*- coding:utf-8 -*-
import time

__author__ = 'yinzishao'
from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view,authentication_classes
from api.serializers import TeacherSerializer,ParentOrderSerializer,MessageSerializer,OrderApplySerializer
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from tutor.http import JsonResponse,JsonError
from api.models import Teacher,AuthUser,ParentOrder,OrderApply,Message,Config
from django.db import transaction
from wechat_auth.helpers import changeBaseToImg,changeObejct,getParentOrderObj,getTeacherObj,changeTime
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening

@login_required()
@api_view(['GET'])
def loginSuc(request):

    teachers = Teacher.objects.all()
    serializer = TeacherSerializer(teachers, many=True)
    return Response(serializer.data)

@login_required()
@api_view(['GET'])
@csrf_exempt
def getInfo(request):
    """
    获取个人信息
    :param request:
    :return:
    """
    user = AuthUser.objects.get(username=request.user.username)
    teacher = user.teacher_set.all()
    parent =  user.parentorder_set.all()
    if len(parent):
        serializer = ParentOrderSerializer(parent[0])
    if len(teacher):
        serializer = TeacherSerializer(teacher[0])
    return Response(serializer.data)

@login_required()
@api_view(['GET','POST'])
@authentication_classes((CsrfExemptSessionAuthentication, BasicAuthentication))
def getTeacherInfo(request):
    """
    获取个人信息
    :param request:
    :return:
    """
    user = AuthUser.objects.get(username=request.user.username)
    if request.method == "GET":
        teacher = user.teacher_set.all()
        if len(teacher):
            serializer = TeacherSerializer(teacher[0])
            result = serializer.data
        else:
            return JsonError("not found")
    elif request.method == "POST":
        tea_id = request.data.get('tea_id',None)
        format = request.data.get('format',None)
        if not tea_id:
            teacher = user.teacher_set.all()
            if len(teacher):
                serializer = TeacherSerializer(teacher[0])
                result = serializer.data
        else:
            teas = Teacher.objects.filter(tea_id = tea_id)
            if len(teas):
                serializer = TeacherSerializer(teas[0])
                result = serializer.data
        if format:
            changeTime(result)
    return Response(result)

@login_required()
@api_view(['GET','POST'])
@authentication_classes((CsrfExemptSessionAuthentication, BasicAuthentication))
def getParentInfo(request):
    """
    获取个人信息
    :param request:
    :return:
    """
    user = AuthUser.objects.get(username=request.user.username)
    if request.method == "GET":
        parents =  user.parentorder_set.all()
        if len(parents):
            serializer = ParentOrderSerializer(parents[0])
            result = serializer.data
        else:
            return JsonError("not found")
    elif request.method == "POST":
        pd_id = request.data.get('pd_id',None)
        format = request.data.get('format',None)
        if not pd_id:
            parents =  user.parentorder_set.all()
            if len(parents):
                serializer = ParentOrderSerializer(parents[0])
                result = serializer.data
            else:
                return JsonError("not found")
        else:
            pds = ParentOrder.objects.filter(pd_id = pd_id)
            if len(pds):
                serializer = ParentOrderSerializer(pds[0])
                result = serializer.data
            else:
                return JsonError("not found")
        if format:
            changeTime(result)
    return Response(result)

@login_required()
@api_view(['POST'])
@authentication_classes((CsrfExemptSessionAuthentication, BasicAuthentication))
def createTeacher(request):
    """
    创建老师
    :param request:
    :return:
    """
    user = AuthUser.objects.get(username=request.user.username)
    teachers = user.teacher_set.all()
    if len(teachers) > 0:
        return JsonError("already existed")
    if request.method == 'POST':
        temp = request.data.dict()  if (type(request.data) != type({})) else request.data
        changeObejct(temp)
        photos = temp.get('teach_show_photo',None)
        if photos:
            temp['teach_show_photo'] = changeBaseToImg(photos)
        temp['create_time']= time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        teacher = Teacher(**temp)
        teacher.wechat = user
        teacher.save()
    return JsonResponse({"wechat_id":teacher.wechat_id})

@login_required()
@api_view(['POST'])
@authentication_classes((CsrfExemptSessionAuthentication, BasicAuthentication))
def updateTeacher(request):
    """
    修改老师
    :param request:
    :return:
    """
    user = AuthUser.objects.get(username=request.user.username)
    teachers = user.teacher_set.all()
    if request.method == 'POST' and len(teachers) > 0:
        temp = request.data.dict()  if (type(request.data) != type({})) else request.data
        changeObejct(temp)
        teacher = user.teacher_set.update(**temp)
        return JsonResponse()
        # 返回更新后的对象
        # serializer = TeacherSerializer(user.teacher_set.all()[0])
        # result = serializer.data
        # getTeacherObj(result)
        # return Response(result)
    return JsonError("not found")

@login_required()
@api_view(['GET'])
@csrf_exempt
def deleteTeacher(request):
    """
    删除
    :param request:
    :return:
    """
    #TODO：删除外键约束
    user = AuthUser.objects.get(username=request.user.username)
    teachers = user.teacher_set.all()
    if len(teachers) > 0:
        teachers[0].delete()
        return JsonResponse()
    return JsonError("not found")

@login_required()
@api_view(['POST'])
@authentication_classes((CsrfExemptSessionAuthentication, BasicAuthentication))
def createParentOrder(request):
    """
    创建家长订单
    :param request:
    :return:
    """
    user = AuthUser.objects.get(username=request.user.username)
    parentorder = user.parentorder_set.all()
    if len(parentorder) > 0:
        return JsonError("already existed")
    if request.method == 'POST':
        temp = request.data.dict()  if (type(request.data) != type({})) else request.data
        changeObejct(temp)
        now = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        temp['create_time']= now
        temp['update_time']= now
        po = ParentOrder(**temp)
        po.wechat = user
        po.save()
    return JsonResponse({"wechat_id":po.wechat_id})

@login_required()
@api_view(['POST'])
@authentication_classes((CsrfExemptSessionAuthentication, BasicAuthentication))
def updateParentOrder(request):
    """
    更新家长订单
    :param request:
    :return:
    """
    user = AuthUser.objects.get(username=request.user.username)
    parentorder = user.parentorder_set.all()
    if request.method == 'POST' and len(parentorder) > 0:
        now = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        temp = request.data.dict()  if (type(request.data) != type({})) else request.data
        changeObejct(temp)
        temp['update_time']= now
        po = user.parentorder_set.update(**temp)
        return JsonResponse()
        # serializer = ParentOrderSerializer(user.parentorder_set.all()[0])
        # result = serializer.data
        # getParentOrderObj(result)
        # return Response(result)
    return JsonError("not found")

@login_required()
@api_view(['GET'])
@authentication_classes((CsrfExemptSessionAuthentication, BasicAuthentication))
def deleteParent(request):
    """
    删除
    :param request:
    :return:
    """
    #TODO：删除外键约束
    user = AuthUser.objects.get(username=request.user.username)
    parentorder = user.parentorder_set.all()
    if len(parentorder) > 0:
        parentorder[0].delete()
        return JsonResponse()
    return JsonError("not found")

#TODO：为家长推荐老师
@login_required()
@api_view(['POST'])
@authentication_classes((CsrfExemptSessionAuthentication, BasicAuthentication))
def getTeachers(request):
    """
        全部老师根据类别获取老师列表
        :param request:
        {
        "size":6,
        "start":0,
        "subject":"语文",
        "grade":1,
        "hot":1,
        }
        :return:
            teacher obejcts
    """
    #TODO:排序与选择
    size = int(request.data.get("size",0))
    start = int(request.data.get("start",0)) * size
    #根据学科排序
    subject = request.data.get("subject", 0)
    #根据年级排序
    grade = request.data.get("grade", 0)
    #根据最新最热排序,两个参数是最热门和最新，默认为最热门（参数为1），然后是最新（参数为2）
    hot = request.data.get("hot",1)
    where = []
    order = '-hot_not'
    if hot == 2:
        order = '-create_time'
    if subject:
        where = ['FIND_IN_SET("'+subject+'",subject)']
    #年级,如果里面是字符串，需要加引号
    if grade:
        where = ['FIND_IN_SET("'+grade+'",grade)']
    teachers = Teacher.objects.extra(where=where).order_by(order)[start:start + size]
    user = AuthUser.objects.get(username=request.user.username)
    pds = user.parentorder_set.all()
    if len(pds) > 0:
        pd = pds[0]
    else:
        return JsonError("家长不存在！请重新填问卷")

    #获取到老师的数据，需要判断是不是报名或者被邀请
    for t in teachers:
        t.isInvited = ''
        #家长主动
        orderApplyA = OrderApply.objects.filter(apply_type=2, pd=pd,tea= t)
        if len(orderApplyA):
            orderApply = orderApplyA[0]
            #完成
            if orderApply.teacher_willing == 1:
                t.isInvited = u'已邀请'
            elif orderApply.teacher_willing == 0:
                t.isInvited = u'已拒绝'
            elif orderApply.teacher_willing == 2:
                t.isInvited = u'已完成'

            t.teacher_willing = orderApplyA[0].teacher_willing
        else:
            #老师主动
            orderApplyB = OrderApply.objects.filter(apply_type=1, pd=pd,tea= t)
            if len(orderApplyB):
                # t.parent_willing = orderApplyB[0].parent_willing
                orderApply = orderApplyB[0]
                if orderApply.parent_willing == 1:
                    t.isInvited = u'已报名'
                elif orderApply.parent_willing == 0:
                    t.isInvited = u'已拒绝'
                elif orderApply.parent_willing == 2:
                    t.isInvited = u'已完成'

    serializer = TeacherSerializer(teachers, many=True)
    teachersData = serializer.data
    getTeacherObj(teachersData,many=True)
    return Response(teachersData)

@login_required()
@api_view(['POST'])
@authentication_classes((CsrfExemptSessionAuthentication, BasicAuthentication))
def getParentOrder(request):
    """
    获取家长列表。家长对于老师的申请处理
    :param request:
    {"start":0,"size":6}
    :return:
    """
    size = int(request.data.get("size",0))
    start = int(request.data.get("start",0)) * size
    user = AuthUser.objects.get(username=request.user.username)
    teas = user.teacher_set.all()
    if len(teas) > 0:
        tea = teas[0]
    else:
        return JsonError("家长不存在！请重新填问卷")
    parentOrders = ParentOrder.objects.all()[start:start + size]
    for po in parentOrders:
        po.isInvited = ''
        #老师主动报名
        orderApplyA = OrderApply.objects.filter(apply_type=1, pd=po,tea= tea)
        if len(orderApplyA):
            orderApply = orderApplyA[0]
            #完成
            if orderApply.parent_willing == 1:
                po.isInvited = u'已报名'
            elif orderApply.parent_willing == 0:
                po.isInvited = u'已拒绝'
            elif orderApply.parent_willing == 2:
                po.isInvited = u'已完成'
        else:
            #家长主动邀请
            orderApplyB = OrderApply.objects.filter(apply_type=2, pd=po,tea= tea)
            if len(orderApplyB):
                # t.parent_willing = orderApplyB[0].parent_willing
                orderApply = orderApplyB[0]
                if orderApply.teacher_willing == 1:
                    po.isInvited = u'已邀请'
                elif orderApply.teacher_willing == 0:
                    po.isInvited = u'已拒绝'
                elif orderApply.teacher_willing == 2:
                    po.isInvited = u'已完成'

    serializer = ParentOrderSerializer(parentOrders, many=True)
    result = serializer.data
    getParentOrderObj(result, many=True)
    return Response(result)

@login_required()
@api_view(['POST'])
@authentication_classes((CsrfExemptSessionAuthentication, BasicAuthentication))
def applyParent(request):
    """
    老师报名家长,取消报名
    :param request:
    {
        "pd_id":2,
        "type": 1/0,
        "expectation":""
    }
    :return:
    """
    #获取家长id
    temp = request.data.dict()  if (type(request.data) != type({})) else request.data
    pd_id = int(temp.get("pd_id", -1))
    method = int(temp.get("type", -1))
    expectation = temp.get("expectation", None)

    user = AuthUser.objects.get(username=request.user.username)
    #查找教师
    teachers = user.teacher_set.all()
    #查找家长订单
    pd = ParentOrder.objects.filter(pd_id=pd_id)
    if len(pd) and len(teachers):
        teacher = teachers[0]
        if method == 1:
            #老师报名家长
            #老师可以报名多个家长!!
            #事务
            try:
                with transaction.atomic():
                    #新建订单
                    order = OrderApply(apply_type=1, pd=pd[0],tea=teacher,parent_willing=1,teacher_willing=2,
                                       pass_not=1,update_time=timezone.now(),expectation=expectation,finished=0)
                    order.save()
                    message_title = teacher.name + u"向您报名!"
                    message_content = teacher.name + u"向您报名!请到“我的老师”处查看详细信息!"
                    #新建消息
                    message = Message(sender=user, receiver=pd[0].wechat,message_title=message_title, message_content=message_content,status=0)
                    message.save()
                    #TODO:推送到微信端

            except Exception,e:
                return JsonError(e.message)
            return JsonResponse()

        elif method == 0 :
            #老师取消报名家长
            try:
                with transaction.atomic():
                    #删除订单
                    order = OrderApply.objects.get(apply_type=1, pd=pd[0],tea=teacher)
                    # order.finished = 1
                    # order.save()
                    order.delete()
                    message_title = teacher.name + u"取消了报名!"
                    message_content = teacher.name + u"取消了报名!"
                    #新建消息
                    message = Message(sender=user, receiver=teacher.wechat, message_title=message_title, message_content=message_content,status=0)
                    message.save()
                    #TODO:推送到微信端

            except Exception,e:
                return JsonError(e.message)
            return JsonResponse()
    else:
        return JsonError(u"不存在家长订单或老师!")

@login_required()
@api_view(['POST'])
@authentication_classes((CsrfExemptSessionAuthentication, BasicAuthentication))
def handleOrder(request):
    """
    处理订单的各种情况，接受或者拒绝老师的报名或者家长的邀请
    :param request:
     {
     "type": 0/1        0：老师处理家长 1：家长处理老师
     "id":1,            如果是老师处理家长，则填对应的pd_id，如果家长处理老师，则填对应的tea_id
     "accept": 0/1      0/1  0：拒绝 1：接受
     }
    :return:
    """
    type = request.data.get('type', None)
    id = request.data.get('id', None)
    accept = request.data.get('accept', None)
    if (type != None and id != None and accept != None):
        user = AuthUser.objects.get(username=request.user.username)
        #家长处理老师
        if (type):
            parentorders = user.parentorder_set.all()
            teas = Teacher.objects.filter(tea_id = id)
            if ( len(parentorders ) and  len(teas) ):
                pd = parentorders[0]
                tea = teas[0]
                orders = OrderApply.objects.filter(apply_type=1, tea=tea, pd=pd)
                if len(orders) :
                    order = orders[0]
                    #对订单进行处理
                    if (accept):
                        order.parent_willing = 2
                        message_title = pd.name + u"接受了你的报名！"
                        message_content = pd.name + u"接受了你的报名！请到“我的家长”处查看详细信息!"
                    else:
                        order.parent_willing = 0
                        message_title = pd.name + u"拒绝了你的报名！"
                        message_content = pd.name + u"拒绝了你的报名！请到“我的家长”处查看详细信息!"
                    #新建消息
                    message = Message(sender=user, receiver=tea.wechat, message_title=message_title, message_content=message_content,status=0)
                    try:
                        with transaction.atomic():
                            message.save()
                            order.finished = 1
                            order.save()
                        #TODO:消息推送到微信端
                    except Exception,e:
                        return JsonError(e.message)
                    return JsonResponse()
                else:
                    return JsonError(u"处理错误，请确定数据无误！")
            else:
                return JsonError(u"处理错误，请确定数据无误！")
        else:
        #老师处理家长
            teas = user.teacher_set.all()
            parentorders = ParentOrder.objects.filter(pd_id = id)
            if ( len(parentorders ) and  len(teas) ):
                pd = parentorders[0]
                tea = teas[0]
                orders = OrderApply.objects.filter(apply_type=2, tea=tea, pd=pd)
                if len(orders) :
                    order = orders[0]
                    #对订单进行处理
                    if (accept):
                        order.teacher_willing = 2
                        message_title = tea.name + u"接受了你的邀请！"
                        message_content = tea.name + u"接受了你的邀请！请到“我的老师”处查看详细信息!"
                    else:
                        order.teacher_willing = 0
                        message_title = tea.name + u"拒绝了你的邀请！"
                        message_content = tea.name + u"拒绝了你的邀请！请到“我的老师”处查看详细信息!"
                    message = Message(sender=user, receiver=pd.wechat, message_title=message_title, message_content=message_content,status=0)
                    try:
                        with transaction.atomic():
                            message.save()
                            order.finished = 1
                            order.save()
                        #消息推送到微信端
                    except Exception,e:
                        return JsonError(e.message)
                    return JsonResponse()
                    #TODO:消息推送到微信端
                else:
                    return JsonError(u"处理错误，请确定数据无误！")
            else:
                return JsonError(u"处理错误，请确定数据无误！")

        pass

    else:
        return JsonError(u"发送的数据有误！")

@login_required()
@api_view(['POST'])
@authentication_classes((CsrfExemptSessionAuthentication, BasicAuthentication))
def inviteTeacher(request):
    """
    家长邀请老师,取消邀请
    :param request:
    {
        "tea_id":2,
        "type":1/0
    }
    :return:
    """
    #TODO:消息提醒
    #获取老师id
    tea_id = request.data.get("tea_id", None)
    type = request.data.get("type", None)
    user = AuthUser.objects.get(username=request.user.username)
    #查找家长订单
    #TODO： 每个家长是否只有一个需求
    parentorders = user.parentorder_set.all()
    #查找教师
    teachers = Teacher.objects.filter(tea_id=tea_id)
    if len(parentorders) and len(teachers):
        parentorder = parentorders[0]
        teacher = teachers[0]
        if type == 1 :
            #家长邀请老师
            #如果家长已经邀请了老师，返回错误
            oa = OrderApply.objects.filter(apply_type=2, pd=parentorder)
            if len(oa) != 0:
                return JsonError("已经邀请了老师")
            #事务
            try:
                with transaction.atomic():
                    #新建订单
                    order = OrderApply(apply_type=2, pd=parentorder,tea=teacher,parent_willing=2,teacher_willing=1,
                                       pass_not=1,update_time=timezone.now(),finished=0)
                    order.save()
                    message_title = parentorder.name + u"向您发起了邀请!"
                    message_content = parentorder.name + u"向您发起了邀请!请到“我的家长”处查看详细信息!"
                    #新建消息
                    message = Message(sender=user, receiver=teacher.wechat, message_title=message_title, message_content=message_content,status=0)
                    message.save()
                    #TODO:推送到微信端

            except Exception,e:
                return JsonError(e.message)
            return JsonResponse()
        elif type == 0 :
            try:
                with transaction.atomic():
                    #取消订单
                    order = OrderApply.objects.get(apply_type=2, pd=parentorder,tea=teacher)
                    order.delete()
                    # order.finished = 1
                    # order.save()
                    message_title = parentorder.name + u"取消了邀请!"
                    message_content = parentorder.name + u"取消了邀请!"
                    #新建消息
                    message = Message(sender=user, receiver=teacher.wechat, message_title=message_title, message_content=message_content,status=0)
                    message.save()
                    #TODO:推送到微信端

            except Exception,e:
                return JsonError(e.message)
            return JsonResponse()
    else:
        return JsonError(u"不存在家长订单或老师!")

def judge(teach_willing,result):
    if teach_willing == 2:
        result = u"愿意"
    elif teach_willing == 0:
        result = u"拒绝"
    return result
@login_required()
@api_view(['GET'])
@authentication_classes((CsrfExemptSessionAuthentication, BasicAuthentication))
def getOrder(request):
    user = AuthUser.objects.get(username=request.user.username)
    t = user.teacher_set.all()
    pd = user.parentorder_set.all()
    oas = None
    if len(t) > 0:
        #老师的订单详情
        oas = OrderApply.objects.filter(tea=t[0])
        results = []
        for oa in oas:
            oa.name= oa.pd.name
            if oa.apply_type == 2:
                oa.type = "parent"
                #家长主动
                oa.result= judge(oa.teacher_willing,u"已邀请") #默认是待处理
                #是否接受邀请
                if oa.teacher_willing == 1:
                    #家长主动，并且教师待处理，应该弹出接受或者拒绝
                    oa.finish = 0
                    pass
                else:
                    #教师已经处理，则直接返回结果。
                    oa.finish = 1
                    pass

            elif oa.apply_type == 1:
                oa.type = "teacher"
                #教师主动
                oa.result= judge(oa.parent_willing,u"已报名")
                #是否取消报名
                if oa.parent_willing == 1:
                    #教师主动，并且家长待处理，应该弹出取消报名
                    oa.finish = 0
                else:
                    #家长已经处理，则直接返回结果。
                    oa.finish = 1
        return Response(OrderApplySerializer(oas,many=True).data)

    elif len(pd) > 0:
        #家长的订单详情
        oas = OrderApply.objects.filter(pd=pd[0])
        results = []
        for oa in oas:
            oa.name= oa.tea.name
            if oa.apply_type == 2:
                oa.type = "parent"
                #家长主动
                oa.result= judge(oa.teacher_willing,u"已邀请")
                #是否取消邀请
                if oa.teacher_willing == 1:
                    #家长主动，并且老师待处理，应该弹出取消邀请
                    oa.finish = 0
                else:
                    #老师已经处理，则直接返回结果。
                    oa.finish = 1
            elif oa.apply_type == 1:
                oa.type = "teacher"
                #教师主动
                oa.result= judge(oa.parent_willing,u"已报名")
                #是否接受报名
                if oa.parent_willing == 1:
                    #教师主动，并且家长待处理，应该弹出取消报名
                    oa.finish = 0
                else:
                    #家长已经处理，则直接返回结果。
                    oa.finish = 1
        return Response(OrderApplySerializer(oas,many=True).data)

    if not oas:
        return Response({"info":"没有订单！"})

@login_required()
@api_view(['POST'])
@authentication_classes((CsrfExemptSessionAuthentication, BasicAuthentication))
def getMsg(request):
    """
    获取消息列表
    :param request:
    {
        "start":0,
        "size":6
    }
    :return:
    """
    size = int(request.data.get("size",0))
    start = int(request.data.get("start",0)) * size
    user = AuthUser.objects.get(username=request.user.username)
    msgs = user.receiver.all()[start:start + size]
    for msg in msgs:
        msg.isDetailed = False
    serializer = MessageSerializer(msgs, many=True)
    result = serializer.data
    for r in result:
        r["status"] = True if r["status"] else False
    return Response(result)

@login_required()
@api_view(['POST'])
@authentication_classes((CsrfExemptSessionAuthentication, BasicAuthentication))
def readMessage(request):
    """
    阅读消息，将status改为１
    :param request:
    {
        "msg_id":1
    }
    :return:
    """
    msg_id = request.data.get("msg_id", None)
    user = AuthUser.objects.get(username=request.user.username)
    msg = Message.objects.filter(msg_id=msg_id, receiver = user).update(status=1)
    return JsonResponse()

@login_required()
@api_view(['GET'])
@authentication_classes((CsrfExemptSessionAuthentication, BasicAuthentication))
def getWechatInfo(request):
    return Response(request.session.get("info",None))

@login_required()
@api_view(['GET','POST'])
@authentication_classes((CsrfExemptSessionAuthentication, BasicAuthentication))
def handleSalary(request):
    if request.method == "GET":
        salary = Config.objects.get(key='salary')
        result = {'value': salary.value}
        return JsonResponse(result)
    elif request.method == "POST":
        salary = Config.objects.get(key='salary')
        value = request.data.get('value', None)
        print value
        if value:
            salary.value = value
            salary.save()
            return JsonResponse()
    return JsonError('出错了！')
