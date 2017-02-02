from datetime import datetime

from pyramid.httpexceptions import exception_response
from pyramid.view import view_config
from pyramid.response import Response
from xml.etree import ElementTree

from consuming_services_apis import Post
from consuming_services_apis.data.memory_db import MemoryDb


@view_config(route_name='soap')
def blog_posts(request):
    print("Processing {} request from {} for the SOAP service: {}, ua: {}".format(
        request.method, get_ip(request), request.url, request.user_agent
    ))

    if "WSDL" in request.GET or "wsdl" in request.GET:
        return Response(body=build_wsdl(request), content_type='application/xml')

    action = request.headers.get('Soapaction').replace('http://tempuri.org/', '').lower().strip("\"")
    if action == 'getpost':
        body = clean_namespaces(request.body.decode('utf-8'))
        dom = ElementTree.fromstring(body)
        return get_post_response(dom, request)
    if action == 'allposts':
        return all_post_response(request)
    if action == 'createpost':
        body = clean_namespaces(request.body.decode('utf-8'))
        print("CREATE VIA:" + body)
        dom = ElementTree.fromstring(body)
        return create_post(dom, request)
    if action == 'updatepost':
        body = clean_namespaces(request.body.decode('utf-8'))
        print("UPDATE VIA:" + body)
        dom = ElementTree.fromstring(body)
        return update_post(dom, request)
    if action == 'deletepost':
        body = clean_namespaces(request.body.decode('utf-8'))
        dom = ElementTree.fromstring(body)
        return delete_post_response(dom, request)

    print("BODY: {}".format(request.body.decode('utf-8')))
    return Response("<TEST />")


def all_post_response(request):
    posts = MemoryDb.get_posts(get_ip(request))

    post_template = """
    <Post>
      <Id>{}</Id>
      <Title>{}</Title>
      <Published>{}</Published>
      <Content>{}</Content>
      <ViewCount>{}</ViewCount>
    </Post>"""

    posts_fragments = [
        post_template.format(p.id, p.title, p.published, p.content, p.view_count)
        for p in posts
        ]

    resp_xml = """<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <AllPostsResponse xmlns="http://tempuri.org/">
              <AllPostsResult>

                {}

              </AllPostsResult>
            </AllPostsResponse>
          </soap:Body>
        </soap:Envelope>""".format("\n".join(posts_fragments))

    return Response(body=resp_xml, content_type='text/xml')


def get_post_response(dom, request):
    id_text = dom.find('Body/GetPost/id').text
    post = MemoryDb.get_post(id_text, get_ip(request))
    if not post:
        raise exception_response(404)

    resp_xml = """<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <GetPostResponse xmlns="http://tempuri.org/">
              <GetPostResult>
                <Id>{}</Id>
                <Title>{}</Title>
                <Published>{}</Published>
                <Content>{}</Content>
                <ViewCount>{}</ViewCount>
              </GetPostResult>
            </GetPostResponse>
          </soap:Body>
        </soap:Envelope>""".format(post.id, post.title, post.published, post.content, post.view_count)

    return Response(body=resp_xml, content_type='text/xml')


def delete_post_response(dom, request):
    id_text = dom.find('Body/DeletePost/id').text
    post = MemoryDb.get_post(id_text, get_ip(request))
    if not post:
        raise exception_response(404)

    if MemoryDb.is_post_read_only(post.id):
        raise exception_response(403)

    MemoryDb.delete_post(post, get_ip(request))

    resp_xml = """<?xml version="1.0" encoding="utf-8"?>
                <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                  <soap:Body>
                    <DeletePostResponse xmlns="http://tempuri.org/" />
                  </soap:Body>
                </soap:Envelope>"""

    return Response(body=resp_xml, content_type='text/xml')


def create_post(dom, request):
    title = dom.find('Body/CreatePost/title').text
    content = dom.find('Body/CreatePost/content').text
    view_count = int(dom.find('Body/CreatePost/viewCount').text)

    now = datetime.now()
    published = "{}-{}-{}".format(now.year, str(now.month).zfill(2), str(now.day).zfill(2))

    post = Post(
        title,
        content,
        view_count,
        published
    )

    MemoryDb.add_post(post, get_ip(request))

    resp_xml = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <CreatePostResponse xmlns="http://tempuri.org/">
      <CreatePostResult>
        <Id>{}</Id>
        <Title>{}</Title>
        <Published>{}</Published>
        <Content>{}</Content>
        <ViewCount>{}</ViewCount>
      </CreatePostResult>
    </CreatePostResponse>
  </soap:Body>
</soap:Envelope>""".format(post.id, post.title, post.published, post.content, post.view_count)

    return Response(body=resp_xml, content_type='text/xml')


def update_post(dom, request):
    post_id = dom.find('Body/UpdatePost/id').text

    post = MemoryDb.get_post(post_id, get_ip(request))
    if not post:
        raise exception_response(404)

    if MemoryDb.is_post_read_only(post_id):
        raise exception_response(403)

    post.title = dom.find('Body/UpdatePost/title').text
    post.content = dom.find('Body/UpdatePost/content').text
    post.view_count = int(dom.find('Body/UpdatePost/viewCount').text)

    resp_xml = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <UpdatePostResponse xmlns="http://tempuri.org/">
      <UpdatePostResult>
        <Id>{}</Id>
        <Title>{}</Title>
        <Published>{}</Published>
        <Content>{}</Content>
        <ViewCount>{}</ViewCount>
      </UpdatePostResult>
    </UpdatePostResponse>
  </soap:Body>
</soap:Envelope>""".format(post.id, post.title, post.published, post.content, post.view_count)

    return Response(body=resp_xml, content_type='text/xml')


def get_ip(request):
    # The real IP is stripped by nginx and the direct request
    # looks like a call from localhost. I've configured nginx
    # to pass the IP it sees under the header X-Real-IP.
    proxy_pass_real_ip = request.headers.get('X-Real-IP')
    if proxy_pass_real_ip:
        return proxy_pass_real_ip
    elif request.remote_addr:
        return request.remote_addr
    else:
        return request.client_addr


def clean_namespaces(body):
    return body \
        .replace('SOAP-ENV:', '') \
        .replace('xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"', '') \
        .replace('xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"', '') \
        .replace('xmlns:ns0="http://schemas.xmlsoap.org/soap/envelope/"', '') \
        .replace('xmlns:ns1="http://tempuri.org/"', '') \
        .replace('xmlns:ns0="http://tempuri.org/"', '') \
        .replace('xmlns:ns1="http://schemas.xmlsoap.org/soap/envelope/"', '') \
        .replace('xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"', '') \
        .replace('soap:', '') \
        .replace('xmlns:xsd="http://www.w3.org/2001/XMLSchema"', '') \
        .replace('xmlns="http://tempuri.org/"', '') \
        .replace('SOAP-ENV:', '') \
        .replace('ns0:', '') \
        .replace('ns1:', '')


def build_wsdl(request):
    wsdl = """
    <wsdl:definitions xmlns:tm="http://microsoft.com/wsdl/mime/textMatching/" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/" xmlns:mime="http://schemas.xmlsoap.org/wsdl/mime/" xmlns:tns="http://tempuri.org/" xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/" xmlns:s="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://schemas.xmlsoap.org/wsdl/soap12/" xmlns:http="http://schemas.xmlsoap.org/wsdl/http/" xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/" targetNamespace="http://tempuri.org/">
    <wsdl:types>
    <s:schema elementFormDefault="qualified" targetNamespace="http://tempuri.org/">
    <s:element name="AllPosts">
    <s:complexType/>
    </s:element>
    <s:element name="AllPostsResponse">
    <s:complexType>
    <s:sequence>
    <s:element minOccurs="0" maxOccurs="1" name="AllPostsResult" type="tns:ArrayOfPost"/>
    </s:sequence>
    </s:complexType>
    </s:element>
    <s:complexType name="ArrayOfPost">
    <s:sequence>
    <s:element minOccurs="0" maxOccurs="unbounded" name="Post" nillable="true" type="tns:Post"/>
    </s:sequence>
    </s:complexType>
    <s:complexType name="Post">
    <s:sequence>
    <s:element minOccurs="0" maxOccurs="1" name="Id" type="s:string"/>
    <s:element minOccurs="0" maxOccurs="1" name="Title" type="s:string"/>
    <s:element minOccurs="1" maxOccurs="1" name="Published" type="s:string"/>
    <s:element minOccurs="0" maxOccurs="1" name="Content" type="s:string"/>
    <s:element minOccurs="1" maxOccurs="1" name="ViewCount" type="s:int"/>
    </s:sequence>
    </s:complexType>
    <s:element name="GetPost">
    <s:complexType>
    <s:sequence>
    <s:element minOccurs="0" maxOccurs="1" name="id" type="s:string"/>
    </s:sequence>
    </s:complexType>
    </s:element>
    <s:element name="GetPostResponse">
    <s:complexType>
    <s:sequence>
    <s:element minOccurs="0" maxOccurs="1" name="GetPostResult" type="tns:Post"/>
    </s:sequence>
    </s:complexType>
    </s:element>
    <s:element name="CreatePost">
    <s:complexType>
    <s:sequence>
    <s:element minOccurs="0" maxOccurs="1" name="title" type="s:string"/>
    <s:element minOccurs="0" maxOccurs="1" name="content" type="s:string"/>
    <s:element minOccurs="1" maxOccurs="1" name="viewCount" type="s:int"/>
    </s:sequence>
    </s:complexType>
    </s:element>
    <s:element name="CreatePostResponse">
    <s:complexType>
    <s:sequence>
    <s:element minOccurs="0" maxOccurs="1" name="CreatePostResult" type="tns:Post"/>
    </s:sequence>
    </s:complexType>
    </s:element>
    <s:element name="UpdatePost">
    <s:complexType>
    <s:sequence>
    <s:element minOccurs="0" maxOccurs="1" name="id" type="s:string"/>
    <s:element minOccurs="0" maxOccurs="1" name="title" type="s:string"/>
    <s:element minOccurs="0" maxOccurs="1" name="content" type="s:string"/>
    <s:element minOccurs="1" maxOccurs="1" name="viewCount" type="s:int"/>
    </s:sequence>
    </s:complexType>
    </s:element>
    <s:element name="UpdatePostResponse">
    <s:complexType>
    <s:sequence>
    <s:element minOccurs="0" maxOccurs="1" name="UpdatePostResult" type="tns:Post"/>
    </s:sequence>
    </s:complexType>
    </s:element>
    <s:element name="DeletePost">
    <s:complexType>
    <s:sequence>
    <s:element minOccurs="0" maxOccurs="1" name="id" type="s:string"/>
    </s:sequence>
    </s:complexType>
    </s:element>
    <s:element name="DeletePostResponse">
    <s:complexType/>
    </s:element>
    </s:schema>
    </wsdl:types>
    <wsdl:message name="AllPostsSoapIn">
    <wsdl:part name="parameters" element="tns:AllPosts"/>
    </wsdl:message>
    <wsdl:message name="AllPostsSoapOut">
    <wsdl:part name="parameters" element="tns:AllPostsResponse"/>
    </wsdl:message>
    <wsdl:message name="GetPostSoapIn">
    <wsdl:part name="parameters" element="tns:GetPost"/>
    </wsdl:message>
    <wsdl:message name="GetPostSoapOut">
    <wsdl:part name="parameters" element="tns:GetPostResponse"/>
    </wsdl:message>
    <wsdl:message name="CreatePostSoapIn">
    <wsdl:part name="parameters" element="tns:CreatePost"/>
    </wsdl:message>
    <wsdl:message name="CreatePostSoapOut">
    <wsdl:part name="parameters" element="tns:CreatePostResponse"/>
    </wsdl:message>
    <wsdl:message name="UpdatePostSoapIn">
    <wsdl:part name="parameters" element="tns:UpdatePost"/>
    </wsdl:message>
    <wsdl:message name="UpdatePostSoapOut">
    <wsdl:part name="parameters" element="tns:UpdatePostResponse"/>
    </wsdl:message>
    <wsdl:message name="DeletePostSoapIn">
    <wsdl:part name="parameters" element="tns:DeletePost"/>
    </wsdl:message>
    <wsdl:message name="DeletePostSoapOut">
    <wsdl:part name="parameters" element="tns:DeletePostResponse"/>
    </wsdl:message>
    <wsdl:portType name="BlogSoap">
    <wsdl:operation name="AllPosts">
    <wsdl:input message="tns:AllPostsSoapIn"/>
    <wsdl:output message="tns:AllPostsSoapOut"/>
    </wsdl:operation>
    <wsdl:operation name="GetPost">
    <wsdl:input message="tns:GetPostSoapIn"/>
    <wsdl:output message="tns:GetPostSoapOut"/>
    </wsdl:operation>
    <wsdl:operation name="CreatePost">
    <wsdl:input message="tns:CreatePostSoapIn"/>
    <wsdl:output message="tns:CreatePostSoapOut"/>
    </wsdl:operation>
    <wsdl:operation name="UpdatePost">
    <wsdl:input message="tns:UpdatePostSoapIn"/>
    <wsdl:output message="tns:UpdatePostSoapOut"/>
    </wsdl:operation>
    <wsdl:operation name="DeletePost">
    <wsdl:input message="tns:DeletePostSoapIn"/>
    <wsdl:output message="tns:DeletePostSoapOut"/>
    </wsdl:operation>
    </wsdl:portType>
    <wsdl:binding name="BlogSoap" type="tns:BlogSoap">
    <soap:binding transport="http://schemas.xmlsoap.org/soap/http"/>
    <wsdl:operation name="AllPosts">
    <soap:operation soapAction="http://tempuri.org/AllPosts" style="document"/>
    <wsdl:input>
    <soap:body use="literal"/>
    </wsdl:input>
    <wsdl:output>
    <soap:body use="literal"/>
    </wsdl:output>
    </wsdl:operation>
    <wsdl:operation name="GetPost">
    <soap:operation soapAction="http://tempuri.org/GetPost" style="document"/>
    <wsdl:input>
    <soap:body use="literal"/>
    </wsdl:input>
    <wsdl:output>
    <soap:body use="literal"/>
    </wsdl:output>
    </wsdl:operation>
    <wsdl:operation name="CreatePost">
    <soap:operation soapAction="http://tempuri.org/CreatePost" style="document"/>
    <wsdl:input>
    <soap:body use="literal"/>
    </wsdl:input>
    <wsdl:output>
    <soap:body use="literal"/>
    </wsdl:output>
    </wsdl:operation>
    <wsdl:operation name="UpdatePost">
    <soap:operation soapAction="http://tempuri.org/UpdatePost" style="document"/>
    <wsdl:input>
    <soap:body use="literal"/>
    </wsdl:input>
    <wsdl:output>
    <soap:body use="literal"/>
    </wsdl:output>
    </wsdl:operation>
    <wsdl:operation name="DeletePost">
    <soap:operation soapAction="http://tempuri.org/DeletePost" style="document"/>
    <wsdl:input>
    <soap:body use="literal"/>
    </wsdl:input>
    <wsdl:output>
    <soap:body use="literal"/>
    </wsdl:output>
    </wsdl:operation>
    </wsdl:binding>
    <wsdl:binding name="BlogSoap12" type="tns:BlogSoap">
    <soap12:binding transport="http://schemas.xmlsoap.org/soap/http"/>
    <wsdl:operation name="AllPosts">
    <soap12:operation soapAction="http://tempuri.org/AllPosts" style="document"/>
    <wsdl:input>
    <soap12:body use="literal"/>
    </wsdl:input>
    <wsdl:output>
    <soap12:body use="literal"/>
    </wsdl:output>
    </wsdl:operation>
    <wsdl:operation name="GetPost">
    <soap12:operation soapAction="http://tempuri.org/GetPost" style="document"/>
    <wsdl:input>
    <soap12:body use="literal"/>
    </wsdl:input>
    <wsdl:output>
    <soap12:body use="literal"/>
    </wsdl:output>
    </wsdl:operation>
    <wsdl:operation name="CreatePost">
    <soap12:operation soapAction="http://tempuri.org/CreatePost" style="document"/>
    <wsdl:input>
    <soap12:body use="literal"/>
    </wsdl:input>
    <wsdl:output>
    <soap12:body use="literal"/>
    </wsdl:output>
    </wsdl:operation>
    <wsdl:operation name="UpdatePost">
    <soap12:operation soapAction="http://tempuri.org/UpdatePost" style="document"/>
    <wsdl:input>
    <soap12:body use="literal"/>
    </wsdl:input>
    <wsdl:output>
    <soap12:body use="literal"/>
    </wsdl:output>
    </wsdl:operation>
    <wsdl:operation name="DeletePost">
    <soap12:operation soapAction="http://tempuri.org/DeletePost" style="document"/>
    <wsdl:input>
    <soap12:body use="literal"/>
    </wsdl:input>
    <wsdl:output>
    <soap12:body use="literal"/>
    </wsdl:output>
    </wsdl:operation>
    </wsdl:binding>
    <wsdl:service name="Blog">
    <wsdl:port name="BlogSoap" binding="tns:BlogSoap">
    <soap:address location="{0}/soap"/>
    </wsdl:port>
    <wsdl:port name="BlogSoap12" binding="tns:BlogSoap12">
    <soap12:address location="{0}/soap"/>
    </wsdl:port>
    </wsdl:service>
    </wsdl:definitions>""".format(request.host_url)

    return wsdl
