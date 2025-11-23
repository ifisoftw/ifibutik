from django.test import TestCase
from .models import Product, ProductImage

class ProductModelTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Product",
            sku="TEST-SKU-001",
            description="Test Description",
            stock_qty=10
        )

    def test_product_creation(self):
        """Test that a product is created correctly with given fields"""
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.sku, "TEST-SKU-001")
        self.assertEqual(self.product.description, "Test Description")
        self.assertEqual(self.product.stock_qty, 10)
        self.assertTrue(self.product.is_active)  # Default value check

    def test_product_str(self):
        """Test the string representation of the product"""
        self.assertEqual(str(self.product), "Test Product")

    def test_sku_uniqueness(self):
        """Test that SKU must be unique"""
        with self.assertRaises(Exception):
            Product.objects.create(
                name="Another Product",
                sku="TEST-SKU-001",  # Same SKU
            )

class ProductImageModelTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Image Test Product",
            sku="IMG-SKU-001"
        )
        self.image1 = ProductImage.objects.create(
            product=self.product,
            image="products/test1.jpg",
            sort_order=2
        )
        self.image2 = ProductImage.objects.create(
            product=self.product,
            image="products/test2.jpg",
            sort_order=1
        )

    def test_image_creation(self):
        """Test that product images are linked correctly"""
        self.assertEqual(self.image1.product, self.product)
        self.assertEqual(self.image1.sort_order, 2)

    def test_image_str(self):
        """Test string representation of product image"""
        self.assertEqual(str(self.image1), "Image Test Product Görseli")

    def test_image_ordering(self):
        """Test that images are ordered by sort_order"""
        images = list(self.product.images.all())
        self.assertEqual(images[0], self.image2)  # sort_order=1
        self.assertEqual(images[1], self.image1)  # sort_order=2
