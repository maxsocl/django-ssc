# coding=utf-8

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from .views import xml_request, socket_request, make_human_readable, form_handler


#TODO make complete tests both for default http handler(without javascript/ajax) and for ajax before override with JS.

class SSCTestCase(TestCase):
    def setUp(self):
        """
        Preconditions
        """
        self.user = User.objects.create_user('max', 'test@mail.com', 'test')
        self.client = Client()


class HTTPRequestTest(SSCTestCase):
    """
    Testing simple HTTP request behaviour.
    """

    def test_unauthorized_access(self):
        """
        Should redirect to login page if not
        authenticated ssc/.
        """
        response = self.client.get('/ssc/', follow=True)
        self.assertEqual(response.templates[0].name, 'ssc/login.html')

    def test_rendering_form(self):
        """
        Should render form.html template /ssc/.
        """
        self.client.login(username='max', password='test')

        response = self.client.get('/ssc/', follow=True)
        self.assertEqual(response.templates[0].name, 'ssc/form.html')
        self.assertTrue('<input type="radio" name="type" value="raw" id="raw" checked>' in response.content)
        self.assertTrue('<input type="radio" name="type" value="comp">' in response.content)
        self.assertTrue('<select style="width:10em;" name="city" id="city">' in response.content)
        self.assertTrue('<select  style="width:5em;" name="point" id="point">' in response.content)
        self.assertTrue('input type="submit" value="Session info"' in response.content)

    #TODO stub make_request and add test for deleting after
    def test_logic(self):
        """
        Testing common logic
        """
        self.client.login(username='max', password='test')

        response = self.client.post('/ssc/', {'login_name': 'KHaRKoV-x00 PoN 1/1/01/01:1.1.99', 'type': 'raw'},
                                    follow=True)
        self.assertTrue('<li>No sessions were found which matched the search criteria.</li>' in response.content)

        response = self.client.post('/ssc/', {'city': 'KHARKOV', 'point': 'X00', 'login_name': '',
                                              'opt1': '001', 'opt2': '001', 'opt3': '001', 'opt4': '001', 'opt5': '001',
                                              'opt6': '01', 'opt7': '099', 'type': 'comp'}, follow=True)
        self.assertTrue('<li>No sessions were found which matched the search criteria.</li>' in response.content)

        response = self.client.post('/ssc/', {'login_name': 'KHARKOV-K13 PON 1/1/04/04:60.1.2', 'type': 'raw'},
                                    follow=True)
        self.assertTrue('KHARKOV-K13 PON 1/1/04/04:60.1.2' in response.content)
        self.assertTrue('Domain=00:02:9b:30:bf:5d' in response.content)
        self.assertTrue(
            '<input type="hidden" name="login_del" value="KHARKOV-K13 PON 1/1/04/04:60.1.2">' in response.content)
        self.assertTrue('<input type="submit" value="Delete" name="submit">' in response.content)
        self.assertTrue('<input type="submit" value="No" name="submit">' in response.content)

        response = self.client.post('/ssc/', {'city': 'KHARKOV', 'point': 'K13', 'login_name': '',
                                              'opt1': '001', 'opt2': '001', 'opt3': '004', 'opt4': '004',
                                              'opt5': '0060',
                                              'opt6': '001', 'opt7': '002', 'type': 'comp'}, follow=True)
        self.assertTrue('KHARKOV-K13 PON 1/1/04/04:60.1.2' in response.content)
        self.assertTrue('Domain=00:02:9b:30:bf:5d' in response.content)
        self.assertTrue(
            '<input type="hidden" name="login_del" value="KHARKOV-K13 PON 1/1/04/04:60.1.2">' in response.content)
        self.assertTrue('<input type="submit" value="Delete" name="submit">' in response.content)
        self.assertTrue('<input type="submit" value="No" name="submit">' in response.content)

        response = self.client.post('/ssc/', {'city': 'KHARKOV', 'point': 'K13', 'login_name': '',
                                              'opt1': '1', 'opt2': '1', 'opt3': '4', 'opt4': '4', 'opt5': '60',
                                              'opt6': '1', 'opt7': '2', 'type': 'comp'}, follow=True)
        self.assertTrue('KHARKOV-K13 PON 1/1/04/04:60.1.2' in response.content)
        self.assertTrue('Domain=00:02:9b:30:bf:5d' in response.content)
        self.assertTrue(
            '<input type="hidden" name="login_del" value="KHARKOV-K13 PON 1/1/04/04:60.1.2">' in response.content)
        self.assertTrue('<input type="submit" value="Delete" name="submit">' in response.content)
        self.assertTrue('<input type="submit" value="No" name="submit">' in response.content)

    def test_syntax_error_handling(self):
        """
        Should return 'Error: ' + ERROR_MSG
        """
        self.client.login(username='max', password='test')

        response = self.client.post('/ssc/', {'login_name': 'test', 'type': 'raw'}, follow=True)
        self.assertTrue('Error: TEST Incorrect input/Syntax error.' in response.content)

        response = self.client.post('/ssc/', {'login_name': 'test', 'type': 'comp'}, follow=True)
        self.assertTrue('Error: Incorrect input/Syntax error.' in response.content)

        response = self.client.post('/ssc/', {'login_name': '', 'type': 'raw'}, follow=True)
        self.assertTrue('Error: Incorrect input/Syntax error.' in response.content)

        response = self.client.post('/ssc/', {'login_name': 'KHaRKV-k05 PoN 1/1/01/1:01.1.1', 'type': 'raw'},
                                    follow=True)
        self.assertTrue('Error: KHARKV-K05 PON 1/1/01/1:01.1.1 Incorrect input/Syntax error.' in response.content)

        response = self.client.post('/ssc/', {'login_name': 'KHaRKoV-x09 PoN 1/1/01/1:01.1.1', 'type': 'raw'},
                                    follow=True)
        self.assertTrue('Error: KHARKOV-X09 PON 1/1/01/1:01.1.1 Incorrect input/Syntax error.' in response.content)

        response = self.client.post('/ssc/', {'login_name': 'KHaRKoV-x00 1/1/01/1:01.1.1', 'type': 'raw'}, follow=True)
        self.assertTrue('Error: KHARKOV-X00 1/1/01/1:01.1.1 Incorrect input/Syntax error.' in response.content)

        response = self.client.post('/ssc/', {'login_name': 'не латин', 'type': 'raw'}, follow=True)
        self.assertTrue('Error: НЕ ЛАТИН Incorrect input/Syntax error.' in response.content)

        response = self.client.post('/ssc/', {'city': 'KHARKOV', 'point': 'X00', 'login_name': '',
                                              'opt1': 'err_val', 'opt2': '1', 'opt3': '01', 'opt4': '01', 'opt5': '1',
                                              'opt6': '1', 'opt7': '99', 'type': 'comp'}, follow=True)
        self.assertTrue('Error: Incorrect input/Syntax error.' in response.content)

        response = self.client.post('/ssc/', {'city': 'KHARKOV', 'point': 'X00', 'login_name': '',
                                              'opt1': '1', 'opt2': 'err_val', 'opt3': '01', 'opt4': '01', 'opt5': '1',
                                              'opt6': '1', 'opt7': '99', 'type': 'comp'}, follow=True)
        self.assertTrue('Error: Incorrect input/Syntax error.' in response.content)

        response = self.client.post('/ssc/', {'city': 'KHARKOV', 'point': 'X00', 'login_name': '',
                                              'opt1': '01', 'opt2': '1', 'opt3': 'err_val', 'opt4': '01', 'opt5': '1',
                                              'opt6': '1', 'opt7': '99', 'type': 'comp'}, follow=True)
        self.assertTrue('Error: Incorrect input/Syntax error.' in response.content)

        response = self.client.post('/ssc/', {'city': 'KHARKOV', 'point': 'X00', 'login_name': '',
                                              'opt1': '01', 'opt2': '1', 'opt3': '01', 'opt4': 'err_val', 'opt5': '1',
                                              'opt6': '1', 'opt7': '99', 'type': 'comp'}, follow=True)
        self.assertTrue('Error: Incorrect input/Syntax error.' in response.content)

        response = self.client.post('/ssc/', {'city': 'KHARKOV', 'point': 'X00', 'login_name': '',
                                              'opt1': '01', 'opt2': '1', 'opt3': '01', 'opt4': '01', 'opt5': 'err_val',
                                              'opt6': '1', 'opt7': '99', 'type': 'comp'}, follow=True)
        self.assertTrue('Error: Incorrect input/Syntax error.' in response.content)

        response = self.client.post('/ssc/', {'city': 'KHARKOV', 'point': 'X00', 'login_name': '',
                                              'opt1': '01', 'opt2': '1', 'opt3': '01', 'opt4': '01', 'opt5': '1',
                                              'opt6': 'err_val', 'opt7': 'error_value', 'type': 'comp'}, follow=True)
        self.assertTrue('Error: Incorrect input/Syntax error.' in response.content)

        response = self.client.post('/ssc/', {'city': 'KHARKOV', 'point': 'X00', 'login_name': '',
                                              'opt1': '01', 'opt2': '1', 'opt3': '01', 'opt4': '01', 'opt5': '1',
                                              'opt6': '1', 'opt7': 'err_val', 'type': 'comp'}, follow=True)
        self.assertTrue('Error: Incorrect input/Syntax error.' in response.content)

        response = self.client.post('/ssc/', {'city': 'KHARKOV', 'point': 'X00', 'login_name': '',
                                              'opt1': '01', 'opt2': '1', 'opt3': '01', 'opt4': '01', 'opt5': '1',
                                              'opt6': '1', 'opt7': 'err_val', 'type': 'raw'}, follow=True)
        self.assertTrue('Error: Incorrect input/Syntax error.' in response.content)

        response = self.client.post('/ssc/', {'login_name': 'KHARKOV-K06 PON 1/1/00/00:0.1.0', 'type': 'raw'},
                                    follow=True)
        self.assertTrue("Error: KHARKOV-K06 PON 1/1/00/00:0.1.0 Incorrect input/Syntax error." in response.content)


'''
class AjaxRequestTest(SSCTestCase):
    """
    Testing ajax HTTP request behaviour.
    """
    #TODO stub socket server response
    def test_logic(self):
        """
        Testing common logic.
        """
        self.client.login(username='max', password='test')

        response = self.client.post('/ssc/', {'login_name': 'KHaRKoV-x00 PoN 1/1/01/01:1.1.99'}, follow=True)
        self.assertEqual(response.content, '[["No sessions were found which matched the search criteria."], false]')

        response = self.client.post('/ssc/', {'login_name': 'KHARKOV-K13 PON 1/1/04/04:60.1.2'}, follow=True)
        self.assertTrue('Domain=00:02:9b:30:bf:5d' in response.content)

    def test_syntax_error_handling(self):
        """
        Should return 'Error: ' + ERROR_MSG
        """
        self.client.login(username='max', password='test')

        response = self.client.post('/ssc/', {}, follow=True)
        self.assertEqual(response.content, '[["Error: Incorrect input/Syntax error."], false]')

        response = self.client.post('/ssc/', {'login_name': 'test'}, follow=True)
        self.assertEqual(response.content, '[["Error: TEST Incorrect input/Syntax error."], false]')

        response = self.client.post('/ssc/', {'login_name': ''}, follow=True)
        self.assertEqual(response.content, '[["Error: Incorrect input/Syntax error."], false]')

        response = self.client.post('/ssc/', {'login_name': 'KHaRKV-k05 PoN 1/1/01/1:01.1.1'}, follow=True)
        self.assertEqual(response.content, '[["Error: KHARKV-K05 PON 1/1/01/1:01.1.1 Incorrect input/Syntax error."], false]')

        response = self.client.post('/ssc/', {'login_name': 'KHaRKoV-x09 PoN 1/1/01/1:01.1.1'}, follow=True)
        self.assertEqual(response.content, '[["Error: KHARKOV-X09 PON 1/1/01/1:01.1.1 Incorrect input/Syntax error."], false]')

        response = self.client.post('/ssc/', {'login_name': 'KHaRKoV-x09 1/1/01/1:01.1.1'}, follow=True)
        self.assertEqual(response.content, '[["Error: KHARKOV-X09 1/1/01/1:01.1.1 Incorrect input/Syntax error."], false]')

        #response = self.client.post('/ssc/', {'login_name': 'не латин'}, follow=True)
        #self.assertEqual(response.content, [["Error: НЕ ЛАТИН Incorrect input/Syntax error."], false]')

        response = self.client.post('/ssc/', {'login_name': 'KHaRKoV-x00 PON 1/1/01/1:1.1'}, follow=True)
        self.assertTrue("Error: KHARKOV-X00 PON 1/1/01/1:1.1 Incorrect input/Syntax error." in response.content)

        response = self.client.post('/ssc/', {'login_name': 'KHARKOV-K06 PON 1/1/00/00:0.1.0'}, follow=True)
        self.assertTrue("Error: KHARKOV-K06 PON 1/1/00/00:0.1.0 Incorrect input/Syntax error." in response.content)
'''


#TODO stub provision server xml interface response
class XMLRequestTest(SSCTestCase):
    """
    Test application exchange via XML Provisioning Server XML interface
    """

    def test_xml(self):
        self.assertTrue('mac-address=00:02:9b:30:bf:5d' in
                        xml_request('KHARKOV-K13 PON 1/1/04/04:60.1.2')[0].values()[0])


#TODO stub socket server response
class SocketRequestTest(SSCTestCase):
    def test_socket(self):
        self.assertTrue('Domain=00:02:9b:30:bf:5d' in
                        make_human_readable(socket_request('max', 'KHARKOV-K13 PON 1/1/04/04:60.1.2'))[0].values()[0])


class FormHandlerTest(TestCase):
    """
    Test form handling.
    """

    class Request(object):
        """
        Request object emulation.
        """
        def __init__(self, _type, **kwargs):
            self.POST = {
                'login_name': kwargs.get('login_name'),
                'type': _type,
                'opt1': kwargs.get('opt1'),
                'opt2': kwargs.get('opt2'),
                'opt3': kwargs.get('opt3'),
                'opt4': kwargs.get('opt4'),
                'opt5': kwargs.get('opt5'),
                'opt6': kwargs.get('opt6'),
                'opt7': kwargs.get('opt7'),
                'city': kwargs.get('city'),
                'point': kwargs.get('point')
            }

    def test_form_handler(self):
        self.assertEqual('KHARKOV-K13 PON 1/1/01/01:1.1.1', form_handler(FormHandlerTest.Request(_type='raw',
                                                                    **{
                                                                        'login_name': 'KHARKOV-K13 PON 1/1/01/01:1.1.1'
                                                                    })))
        self.assertEqual(['Error: Incorrect input/Syntax error.'], form_handler(FormHandlerTest.Request(_type='raw',
                                                                                **{'login_name': ''})))
        self.assertEqual('KHARKOV-K13 PON 1/1/01/01:1.1.1', form_handler(FormHandlerTest.Request(_type='comp',
                                                                         **{
                                                                             'login_name': '',
                                                                             'opt1': '1',
                                                                             'opt2': '1',
                                                                             'opt3': '1',
                                                                             'opt4': '1',
                                                                             'opt5': '1',
                                                                             'opt6': '1',
                                                                             'opt7': '1',
                                                                             'city': 'KHARKOV',
                                                                             'point': 'K13'
                                                                         })))
        self.assertEqual(['Error: Incorrect input/Syntax error.'], form_handler(FormHandlerTest.Request(_type='comp',
                                                                                **{
                                                                                    'login_name': '',
                                                                                    'opt1': '',
                                                                                    'opt2': '',
                                                                                    'opt3': '',
                                                                                    'opt4': '',
                                                                                    'opt5': '',
                                                                                    'opt6': '',
                                                                                    'opt7': '',
                                                                                    'city': 'KHARKOV',
                                                                                    'point': 'K13'
                                                                                })))
        self.assertEqual(['Error: Incorrect input/Syntax error.'], form_handler(FormHandlerTest.Request(_type='comp',
                                                                                **{
                                                                                    'login_name': '',
                                                                                    'opt1': '1',
                                                                                    'opt2': '1',
                                                                                    'opt3': '1',
                                                                                    'opt4': '1',
                                                                                    'opt5': '1',
                                                                                    'opt6': '1',
                                                                                    'opt7': '1',
                                                                                    'city': '',
                                                                                    'point': 'K13'
                                                                                })))
        self.assertEqual(['Error: Incorrect input/Syntax error.'], form_handler(FormHandlerTest.Request(_type='comp',
                                                                                **{
                                                                                    'login_name': '',
                                                                                    'opt1': '1',
                                                                                    'opt2': '1',
                                                                                    'opt3': '1',
                                                                                    'opt4': '1',
                                                                                    'opt5': '1',
                                                                                    'opt6': '1',
                                                                                    'opt7': '1',
                                                                                    'city': 'KHARKOV',
                                                                                    'point': ''
                                                                                })))
