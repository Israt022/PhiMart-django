from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from product.models import Product,Category,Review
from product.serializers import ProductSerializer,CategorySerializer,ReviewSerializer
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.mixins import CreateModelMixin,ListModelMixin
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from product.filters import ProductFilter
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.pagination import PageNumberPagination
from product.paginations import DefaultPagination
# Create your views here.
# Use 
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    # filterset_fields = ['category_id','price']
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    search_fields = ['name','description','category__name']
    ordering_fields = ['price','updated_at']
    
    
    # def get_queryset(self):
    #     queryset = Product.objects.all()
    #     category_id = self.request.query_params.get('category_id')
        
    #     if category_id is not None:
    #         queryset = Product.objects.filter(category_id=category_id)
    #     return queryset
    
    def destroy (self,request,*args, **kwargs):
        product = self.get_object()
        if product.stock > 10:
            return Response({'messgae' : 'Product with stock more than 10 could not ne deleted'})
        self.perform_destroy(product)
        return Response(status=status.HTTP_204_NO_CONTENT)
# Use 
class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.annotate(product_count=Count('products')).all()
    serializer_class = CategorySerializer
    
    
# Use 
class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}  
    
@api_view(['GET','POST'])
def view_products(request):
    if request.method == 'GET':
        products = Product.objects.select_related('category').all()
        serializer = ProductSerializer(products,many = True)
        return Response(serializer.data)
    if request.method == 'POST':
        serializer = ProductSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    
class ViewProducts(APIView):
    def get(self,request):
        products = Product.objects.select_related('category').all()
        serializer = ProductSerializer(products,many = True)
        return Response(serializer.data)
    def post(self,request):
        serializer = ProductSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    
class ProductList(ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # def get_queryset(self):
    #     return Product.objects.select_related('category').all()
    # def get_serializer_class(self):
    #     return ProductSerializer

@api_view(['GET', 'PUT', 'DELETE'])
def view_specific_product(request, id):
    if request.method == 'GET':
        product = get_object_or_404(Product, pk=id)
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    if request.method == 'PUT':
        product = get_object_or_404(Product, pk=id)
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    if request.method == 'DELETE':
        product = get_object_or_404(Product, pk=id)
        copy_of_product = product
        product.delete()
        serializer = ProductSerializer(copy_of_product)
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
    
class ViewSpecificProduct(APIView):
    def get(self,request,id):
        product = get_object_or_404(Product, pk=id)
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    def put(self,request,id):
        product = get_object_or_404(Product, pk=id)
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    def delete(self,request,id):
        product = get_object_or_404(Product, pk=id)
        copy_of_product = product
        product.delete()
        serializer = ProductSerializer(copy_of_product)
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

class ProductDetails(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'id'
    
    # def delete(self,request,id):
    #     product = get_object_or_404(Product, pk=id)
    #     if product.stock > 10:
    #         return Response({'messgae' : 'Product with stock more than 10 could not ne deleted'})
    #     product.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)

 
@api_view()
def view_categories(request):
    categories = Category.objects.annotate(product_count=Count('products'))
    serializer = CategorySerializer(categories,many=True)
    return Response(serializer.data)

class ViewCategories(APIView):
    def get(self,reqest):
        categories = Category.objects.annotate(product_count=Count('products')).all()
        serializer = CategorySerializer(categories,many=True)
        return Response(serializer.data)
    def post(self,request):
        serializer = CategorySerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)

class CategoryList(ListCreateAPIView):
    queryset = Category.objects.annotate(product_count=Count('products')).all()
    serializer_class = CategorySerializer

@api_view()
def view_spacific_category(request,pk):
    category = get_object_or_404(Category,pk=pk)
    serializer = CategorySerializer(category)
    return Response(serializer.data)

class ViewSpecificCategory(APIView):
    def get(self,request,id):
        category = get_object_or_404(Category.objects.annotate(product_count=Count('products')).all(),pk=id)
        serializer = CategorySerializer(category)
        return Response(serializer.data)
    def put(self,request,id):
        category = get_object_or_404(Category.objects.annotate(product_count=Count('products')).all(),pk=id)
        serializer = CategorySerializer(category,data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    def delete(self,request,id):
        category = get_object_or_404(Category.objects.annotate(product_count=Count('products')).all(),pk=id)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class CategoryDetails(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.annotate(product_count=Count('products')).all()
    serializer_class = CategorySerializer