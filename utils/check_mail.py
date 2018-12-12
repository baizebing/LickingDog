#!/usr/bin/python
# -*- coding: UTF-8 -*-
import poplib
import time
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr


# indent用于缩进显示:
def print_info(msg, indent=0):
    file_for_write = '/home/hetao/licking_dog/LickingDog/mail_dir/chat_%s.txt'% (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    if indent == 0:
        # 邮件的From, To, Subject存在于根对象上:

        title_info = ""
        for header in ['From', 'To', 'Subject']:
            value = msg.get(header, '')
            if value:
                if header=='Subject':
                    # 需要解码Subject字符串:
                    value = decode_str(value)
                    if "聊天记录" not in value:
                        print("%s not a chat mail \n" % value)
                        return
                else:
                    # 需要解码Email地址:
                    hdr, addr = parseaddr(value)
                    name = decode_str(hdr)
                    value = u'%s <%s>' % (name, addr)
            title_info += '%s%s: %s\n' % ('  ' * indent, header, value)
        f = open(file_for_write, "wb")
        print(title_info)
        f.write(title_info.encode('utf-8'))
    if (msg.is_multipart()):
        # 如果邮件对象是一个MIMEMultipart,
        # get_payload()返回list，包含所有的子对象:
        parts = msg.get_payload()
        for n, part in enumerate(parts):
            index = u'%spart %s' % (u'  ' * indent, n)
            print(index)
            indent_str = u'%s--------------------' % (u'  ' * indent)
            print(indent_str)
            # 递归打印每一个子对象:
            print_info(part, indent + 1)
    else:
        # 邮件对象不是一个MIMEMultipart,
        # 就根据content_type判断:
        f = open(file_for_write, "wb")
        content_type = msg.get_content_type()
        if content_type=='text/plain' or content_type=='text/html':
            # 纯文本或HTML内容:
            content = msg.get_payload(decode=True)
            # 要检测文本编码:
            charset = guess_charset(msg)
            if charset:
                content = content.decode(charset)
            content_str = u'%sText: %s' % (u'  ' * indent, content + u'...')
            print(content_str)
            f.write(content_str.encode('utf-8'))
        else:
            # 不是文本,作为附件处理
            content_type_str = u'%sAttachment: %s' % (u'  ' * indent, content_type)
            f.write(content_type_str.encode('utf-8'))

def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value

def guess_charset(msg):
    # 先从msg对象获取编码:
    charset = msg.get_charset()
    if charset is None:
        # 如果获取不到，再从Content-Type字段获取:
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos + 8:].strip()
    return charset

if __name__  == "__main__":

    # 输入邮件地址, 口令和POP3服务器地址:
    email = '18618496905@163.com'
    password = 'id19960106id'
    pop3_server = 'pop.163.com'

    # 连接到POP3服务器:
    server = poplib.POP3(host=pop3_server)
    # 可以打开或关闭调试信息:
    # server.set_debuglevel(1)
    # 可选:打印POP3服务器的欢迎文字:
    # print(server.getwelcome().decode('utf-8'))
    # 身份认证:
    server.user(email)
    server.pass_(password)
    # stat()返回邮件数量和占用空间:
    # print('Messages: %s. Size: %s' % server.stat())
    # list()返回所有邮件的编号:
    resp, mails, octets = server.list()
    # 可以查看返回的列表类似['1 82923', '2 2184', ...]
    # print(mails)
    # 获取最新一封邮件, 注意索引号从1开始:
    index = len(mails)
    if index >= 1:
        for i in range(index):
            resp, lines, octets = server.retr(i+1)
            # lines存储了邮件的原始文本的每一行,
            # 可以获得整个邮件的原始文本:
            msg_content = b'\r\n'.join(lines).decode('utf-8')
            # 稍后解析出邮件:
            msg = Parser().parsestr(msg_content)
            print_info(msg)
            server.dele(i+1)
            time.sleep(1)
    # 可以根据邮件索引号直接从服务器删除邮件:
    # 关闭连接:
    server.quit()

