import { BrandService } from './../../p-layout/shared/services/brand.service';
import { LayoutAPIService } from './../../p-layout/shared/services/layout-api.service';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Subject, Subscription, pluck, takeUntil, tap } from 'rxjs';
import { DTOProduct } from '../shared/dto/DTOProduct.dto';
import { ProductAPIService } from '../shared/services/product-api.service';
import { HttpHeaders, HttpClient } from '@angular/common/http';
import { CategoryService } from '../../p-layout/shared/services/category.service';

@Component({
  selector: 'product-list',
  templateUrl: './product-list.component.html',
  styleUrls: ['./product-list.component.scss'],
})
export class ProductListComponent implements OnInit {
  //Data declarations
  isLoading = true;
  productList: DTOProduct[] = [];
  categoryName: string = '';
  keyFilter: string = 'Kết quả tìm kiếm'; // load search key
  totalProduct: string = `{ ${0} } Sản Phẩm`; // load total product
  arrlabelFilter: any[] = [];
  listDataASC = ['All', 'Giá ( Thấp - Cao )', 'Giá ( Cao - Thấp )'];
  selectedValue = 'All';
  allDataDropdowns: any[] = [];
  query = '';
  sortQuey = '';
  priceQuery = [];
  //Subscription declarations
  getListProduct_sst: Subscription;
  ngUnsubscribe = new Subject<void>();

  //Paginate declarations
  page = 1;
  pageSize = 0;
  totalItems = 0;

  constructor(
    private layoutAPIService: LayoutAPIService,
    private route: ActivatedRoute,
    private productService: ProductAPIService,
    private categoryService: CategoryService,
    private BrandService: BrandService
  ) {}

  ngOnInit() {
    this.route.params
      .pipe(
        pluck('categoryname'),
        tap((value) => (this.categoryName = value))
      )
      .subscribe((res) => {
        console.log('this.categoryName', res);
        this.getProducts();
      });

    this.getProducts();
    this.handleGetFilter();
    this.productService
    .getQueryFilter()
    .pipe(takeUntil(this.ngUnsubscribe))
    .subscribe((res) => {
      this.query = res;
      console.log('this.query obssss', this.query);
      if (this.query.length > 0) {
        this.handleQuery(this.sortQuey);
      }
    });
    console.log(this.categoryName);
  }

  getProducts(
    headers = new HttpHeaders({ CategoryName: `${this.categoryName}` }),
    url = '/api/v1/product'
  ) {
    this.isLoading = true;
    let totalProduct = 0;
    this.getListProduct_sst = this.layoutAPIService
      .GetFilterProducts(url, headers)
      .subscribe((res) => {
        this.productList = [...res.Data];
        this.pageSize = res.PageSize;
        this.totalItems = res.TotalProduct;
        totalProduct = res.TotalProduct;
      });
    const loadingInterval = setInterval(() => {
      console.log(' loading...');
    }, 200); // Simulate loading every 0.1 second
    setTimeout(() => {
      clearInterval(loadingInterval);
      console.log('totalProduct set', totalProduct);
      this.totalProduct = `{ ${totalProduct} } Sản Phẩm`;

      this.isLoading = false; // Turn off loading
    }, 200);
  }

  setCategories() {
    this.categoryService
      .getData(1, 100)
      .pipe(takeUntil(this.ngUnsubscribe))
      .subscribe((res) => {
        const categories = res.Data;
        let arr = [];
        categories.forEach((cate) => {
          arr.push({
            type: 'checkbox',
            inputValue: cate.CategoryName,
            field: 'CategoryName',
            labelName: cate.CategoryName,
          });
        });
        var obj = {
          titleFilter: 'Category',
          dataItems: [...arr],
        };
        this.allDataDropdowns.push(obj);
        console.log('this.CategoryFilter', obj);
      });
  }

  setBrands() {
    this.BrandService.getData(1, 100, '')
      .pipe(takeUntil(this.ngUnsubscribe))
      .subscribe((res) => {
        const brands = res.Data;
        let arr = [];
        brands.forEach((b) => {
          arr.push({
            type: 'checkbox',
            inputValue: b.BrandName,
            field: 'BrandName',
            labelName: b.BrandName,
          });
        });
        var obj = {
          titleFilter: 'Brand',
          dataItems: [...arr],
        };
        this.allDataDropdowns.push(obj);
      });
  }

  handleGetFilter() {
    this.productService.getArrlabelFilter().subscribe((arr) => {
      this.arrlabelFilter = arr;
    });
    this.setCategories();
    this.setBrands();
  }
  handlePageChange(event: any) {
    this.page = event;
    console.log(event);
    const headers = new HttpHeaders({
      CurrentPage: `${this.page}`,
    });
    this.getProducts(headers);
  }

  handleURL(event: string) {
    this.query += event;
    console.log(this.query);
    const arrQuery = this.query.split(',').filter(Boolean);
    let headers = new HttpHeaders();
    console.log('event filter URL', arrQuery);

    arrQuery.forEach((item) => {
      const [key, value] = item.split(':'); // Split the item into key and value
      if (key && value) {
        const existingValue = headers.get(key.trim());
        if (existingValue) {
          headers = headers.set(key.trim(), `${existingValue},${value.trim()}`);
        } else {
          headers = headers.set(key.trim(), value.trim());
        }
      }
    });
    console.log('event filter URL', headers);

    // this.getProducts(headers);
  }

  handleCloseFilter(item) {
    this.arrlabelFilter = this.arrlabelFilter.filter(
      (i) => i.labelName !== item.labelName
    );
    console.log(this.arrlabelFilter);
    this.productService.setRemoveItem([item.labelName]);
    // const arrQuery = this.query.split(',').filter(Boolean);
    // this.query = arrQuery
    //   .filter((i) => !i.includes(`:${item.labelName}`))
    //   .join(',');
    //calling the get product again
    console.log('handle close filter', this.query);
    this.productService.setArrlabelFilter(this.arrlabelFilter);
  }
  handleDropdownSelectionChange(event) {
    if (event == 'Giá ( Thấp - Cao )') {
      this.sortQuey = 'ASC';
      this.handleQuery('ASC');
    } else if (event == 'Giá ( Cao - Thấp )') {
      this.sortQuey = 'DESC';
      this.handleQuery('DESC');
    } else {
      this.sortQuey = '';
      this.handleQuery('');
    }
  }

  handleFilterPrice(event: any) {
    this.priceQuery = event;
    console.log('this.priceQuery', this.priceQuery);
    this.handleQuery(this.sortQuey, this.priceQuery);
  }

  handleQuery(sort = '', price = []) {
    const arrQuery = this.query.split(',').filter(Boolean);
    if (sort.length > 0) {
      arrQuery.push(`Sort:${sort}`);
    }
    let headers = new HttpHeaders();

    arrQuery.forEach((item) => {
      const [key, value] = item.split(':'); // Split the item into key and value
      if (key && value) {
        const existingValue = headers.get(key.trim());
        if (existingValue) {
          headers = headers.set(key.trim(), `${existingValue},${value.trim()}`);
        } else {
          headers = headers.set(key.trim(), value.trim());
        }
      }
    });
    if (price.length > 0) {
      headers = headers.set(
        'Price',
        `gte:${price[0] || 0},lte:${price[1] || 0}`
      );
    }
    this.getProducts(headers);
  }
}
