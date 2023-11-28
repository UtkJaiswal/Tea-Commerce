from rest_framework import generics
from .models import *
from .serializers import *
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta
import jwt
from rest_framework import permissions
from vendor.models import *
from copy import deepcopy
from django.shortcuts import get_object_or_404


def generate_token(id,email,password,role):
    payload = {
        'id' : id,
        'email' : email,
        'password' : password,
        'exp': datetime.utcnow() + timedelta(minutes=30),
        'role':role
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS512')
    return token

def handle_auth_exceptions(func):
    def wrapper(*args, **kwargs):
        result = {}
        result['status'] =  'NOK'
        result['valid']  =  False
        result['result'] = {"message":"Unauthorized access","data" :{}}
        try:
            request = args[1]  # Assuming the request is the second argument
            header_access_token = request.META.get('HTTP_AUTHORIZATION')
            if not header_access_token:
                result['result']['message'] = "Authorization header missing"
                return Response(result,status=status.HTTP_400_BAD_REQUEST)
            splited_access_token = header_access_token.split(' ')
            if len(splited_access_token) != 2:
                result['result']['message'] = "Authorization header missing"
                return Response(result,status=status.HTTP_400_BAD_REQUEST)
            access_token = splited_access_token[1]
            user_data = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS512"])
            if not user_data or 'email' not in user_data:
                result['result']['message'] = "User data not found in token"
                return Response(result,status=status.HTTP_401_UNAUTHORIZED)
            request.user_data = user_data
            return func(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            result['result']['message'] = "Token expired. Please login again"
            return Response(result, status=status.HTTP_401_UNAUTHORIZED)
        except CustomUser.DoesNotExist:
            result['result']['message'] = "User not found"
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            result['result']['message'] = str(e)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            result['result']['message'] = str(e)
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return wrapper


class CreateUser(APIView):
    def post(self, request):
        result = {}
        result['status'] = 'NOK'
        result['valid'] = False
        result['result'] = {"message": "Unauthorized access", "data": {}}
        try:
            
            data = deepcopy(request.data)
            data['role'] = "buyer"
            serializer = UserSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                result['status'] = "OK"
                result['valid'] = True
                result['result']['message'] = 'User Created successfully !'
                result['result']['data'] = serializer.data
                return Response(result, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            result['result']['message'] = f'Error:{str(e)}'
            return Response(result,status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class Login(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        result = {}
        result['status'] = 'NOK'
        result['valid'] = False
        result['result'] = {"message": "Unauthorized access", "data": {}}

        if serializer.is_valid():
            try:
                email = serializer.validated_data['email']
                password = serializer.validated_data['password']
                user_data       = CustomUser.objects.filter(email=email).first()

                if user_data is None:
                    result['result']['message'] = "Email not registered with us. Please sign up first to login."
                    return Response(result, status=status.HTTP_401_UNAUTHORIZED)
                
                else:
                    if user_data.check_password(password) == False:
                        result['result']['message'] = "Incorrect Password"
                        return Response(result, status=status.HTTP_401_UNAUTHORIZED)
                    else:
                        reponse_data = {
                            'id' : user_data.id,
                            'name' : user_data.name,
                            'email': user_data.email,
                            'role':user_data.role
                        }

                        token = generate_token(user_data.id,email, password,user_data.role)

                        result['status']            =   "OK"
                        result['result']['message'] =   "Logged in successfully"
                        result['valid']             =    True

                        result['result']['data']['user_info'] = reponse_data
                        result['result']['data']['token'] = token
                        return Response(result,status=status.HTTP_200_OK)
            except Exception as e:
                # Response data
                result['status'] = 'NOK'
                result['valid'] = False
                result['result']['message'] = f"Error :{str(e)}"
                # Response data
                return Response(result, status=status.HTTP_204_NO_CONTENT)

        else:
                result['result']['message'] = (list(serializer.errors.keys())[
                    0]+' - '+list(serializer.errors.values())[0][0]).capitalize()
                return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)




# class Logoutview(APIView):
#     def get(self, request):
#         result = {}
#         result['status'] = 'NOK'
#         result['valid'] = False
#         result['result'] = {"message": "Unauthorized access", "data": []}
#         if request.user.is_authenticated:
#             try:
#                 request._auth.delete()
#             except:
#                 # Response data
#                 result['status'] = "NOK"
#                 result['valid'] = False
#                 result['result']['message'] = 'Error while logging out'
#                 # Response data
#                 return Response(result, status=status.HTTP_200_OK)
#             # Response data
#             result['status'] = "OK"
#             result['valid'] = True
#             result['result']['message'] = 'Logout successfully !'
#             # Response data
#             return Response(result, status=status.HTTP_200_OK)
        

class VendorsList(APIView):
    @handle_auth_exceptions
    def get(self, request):
        result = {}
        result['status'] = 'NOK'
        result['valid'] = False
        result['result'] = {"message": "Unauthorized access", "data": []}

        try:
            user = request.user_data
            if user['role'] == "buyer":
                vendors_list = Vendor.objects.filter(user__role='vendor').values('user__name', 'tea__name')

                result['status'] = "OK"
                result['valid'] = True
                result['result']['message'] = 'Vendors list fetched successfully !'
                result['result']['data'] = vendors_list

                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_401_UNAUTHORIZED)
            
        except Exception as e:
            result['result']['message'] = f"Error fetching data: {str(e)}"
            return Response(result,status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FetchTeaPrice(APIView):
    @handle_auth_exceptions
    def get(self, request):
        result = {}
        result['status'] = 'NOK'
        result['valid'] = False
        result['result'] = {"message": "Unauthorized access", "data": []}

        try:
            vendor_id = request.query_params.get('vendor_id')
            user = request.user_data

            if user['role'] == "buyer":
                tea_price = Tea.objects.filter(vendor__id =  vendor_id).values('price').first()
                result['status'] = "OK"
                result['valid'] = True
                result['result']['message'] = 'Tea price fetched successfully !'
                result['result']['data'] = tea_price

                return Response(result,status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_401_UNAUTHORIZED)
            
        except Exception as e:
            result['result']['message'] = f"Error fetching data: {str(e)}"
            return Response(result,status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PostTransaction(APIView):
    @handle_auth_exceptions
    def post(self, request):
        result = {}
        result['status'] = 'NOK'
        result['valid'] = False
        result['result'] = {"message": "Unauthorized access", "data": []}

        try:
            user = request.user_data
            if user['role'] == "buyer":
                from_user = get_object_or_404(CustomUser, id=user['id'])
                vendor_id = request.data['vendor_id']
                # vendor_id = Vendor.objects.get(user__id = user['id']).id
                amount = request.data['amount']
                shipping_address = request.data['shipping_address']
                quantity = request.data['quantity']

                vendor = Vendor.objects.get(id=vendor_id)

                transaction = Transaction.objects.create(
                    from_user = from_user,
                    to_user = vendor,
                    amount = amount,
                    shipping_address = shipping_address,
                    quantity = quantity
                )

                result['status'] = 'OK'
                result['valid'] = True
                result['result'] = {
                    'message': 'Transaction created successfully',
                    'data': {'transaction_id': transaction.id}
                }
                return Response(result, status=status.HTTP_201_CREATED)
            else:
                result['result']['message'] = 'Unauthorized or invalid user'
                return Response(result, status=status.HTTP_403_FORBIDDEN)
            
        except Vendor.DoesNotExist:
            result['result']['message'] = 'Vendor with the provided ID does not exist'
            return Response(result, status=status.HTTP_404_NOT_FOUND)

        except KeyError:
            result['result']['message'] = 'Incomplete data provided'
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            result['result']['message'] = f"Error fetching data: {str(e)}"
            return Response(result,status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        



