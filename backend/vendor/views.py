from django.shortcuts import render
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
from user.views import generate_token, handle_auth_exceptions
from user.serializers import UserSerializer

# Create your views here.
class CreateUser(APIView):
    def post(self, request):
        result = {}
        result['status'] = 'NOK'
        result['valid'] = False
        result['result'] = {"message": "Unauthorized access", "data": {}}

        try:
            data = deepcopy(request.data)
            data['role'] = "vendor"
            user_serializer = UserSerializer(data=data)

            if user_serializer.is_valid():
                user_instance = user_serializer.save()
                vendor_data = {
                    'user': user_instance.id
                }

                vendor_serializer = VendorSerializer(data=vendor_data)

                if vendor_serializer.is_valid():
                    vendor_serializer.save()
                    result['status'] = "OK"
                    result['valid'] = True
                    result['result']['message'] = 'Vendor Created successfully!'
                    result['result']['data'] = vendor_serializer.data
                    return Response(result, status=status.HTTP_201_CREATED)

                else:
                    user_instance.delete()  # Delete the user instance if Vendor creation fails
                    return Response(vendor_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
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
        

class CreateTeaDescription(APIView):
    @handle_auth_exceptions
    def post(self, request):
        result = {}
        result['status'] = 'NOK'
        result['valid'] = False
        result['result'] = {"message": "Unauthorized access", "data": {}}

        try:
            user = request.user_data
            if user['role'] == "vendor":
                price = request.data['price']
                quantity = request.data['quantity']
                name = request.data['name']

                tea_desc = Tea.objects.create(
                    price = price,
                    quantity = quantity,
                    name = name
                )
                tea_desc_dict = {
                    'id': tea_desc.id,
                    'name': tea_desc.name,
                    'price': tea_desc.price,
                    'quantity': tea_desc.quantity
                }

                vendor = Vendor.objects.get(user__id = user['id'])
                vendor.tea = tea_desc
                vendor.save()

                result['status'] = 'OK'
                result['valid'] = True
                result['result'] = {
                    'message': 'Tea description created successfully',
                    'data': tea_desc_dict
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


class GetTeaDescription(APIView):
    @handle_auth_exceptions
    def get(self, request):
        result = {}
        result['status'] = 'NOK'
        result['valid'] = False
        result['result'] = {"message": "Unauthorized access", "data": {}}

        try:
            user = request.user_data
            
            if user['role'] == "vendor":
                user_id = user['id']

                vendor = Vendor.objects.get(user__id = user_id)

                tea = vendor.tea
                tea_id = tea.id
                tea_name = tea.name
                tea_price = tea.price
                tea_quantity = tea.quantity

                result['status'] = 'OK'
                result['valid'] = True
                result['result'] = {
                    'message': 'Tea object fetched successfully',
                    'data': {
                        'tea_id':tea_id,
                        'tea_name': tea_name,
                        'tea_price': tea_price,
                        'tea_quantity': tea_quantity,
                    }
                }
                return Response(result, status=status.HTTP_200_OK)
            return Response(result, status=status.HTTP_401_UNAUTHORIZED)
        
        except Vendor.DoesNotExist:
            result['result']['message'] = 'Vendor associated with the provided user ID does not exist'
            return Response(result, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            result['result']['message'] = f"Error fetching tea object: {str(e)}"
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class UpdateTeaDescription(APIView):
    @handle_auth_exceptions
    def patch(self, request):
        result = {}
        result['status'] = 'NOK'
        result['valid'] = False
        result['result'] = {"message": "Unauthorized access", "data": {}}

        try:
            user = request.user_data
            tea_id = request.query_params.get('tea_id')

            if user['role'] == 'vendor':
                tea = Tea.objects.get(pk=tea_id)
                if 'name' in request.data:
                    tea.name = request.data['name']
                if 'price' in request.data:
                    tea.price = request.data['price']
                if 'quantity' in request.data:
                    tea.quantity = request.data['quantity']

                tea.save()

                result['status'] = 'OK'
                result['valid'] = True
                result['result'] = {
                    'message': 'Tea description updated successfully',
                    'data': {
                        'id': tea.id,
                        'name': tea.name,
                        'price': tea.price,
                        'quantity': tea.quantity
                    }
                }
                return Response(result, status=status.HTTP_200_OK)
            else:
                result['result']['message'] = 'Unauthorized or invalid user'
                return Response(result, status=status.HTTP_403_FORBIDDEN)
            
        except Tea.DoesNotExist:
            result['result']['message'] = 'Tea with the provided ID does not exist'
            return Response(result, status=status.HTTP_404_NOT_FOUND)

        except KeyError:
            result['result']['message'] = 'Incomplete data provided'
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            result['result']['message'] = f"Error updating tea description: {str(e)}"
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



