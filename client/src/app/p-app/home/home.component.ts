import { ProductService } from './../p-layout/shared/services/product.service';
import { Component, OnDestroy, OnInit, SkipSelf } from '@angular/core';
import { LayoutAPIService } from '../p-layout/shared/services/layout-api.service';
import { Subject, Subscription, concatMap, takeUntil, tap } from 'rxjs';
import { CategoryService } from '../p-layout/shared/services/category.service';
import { DTOResponse } from '../p-layout/shared/dto/DTOResponse';
import { DTOProductFilter } from '../p-layout/shared/dto/DTOProductFilter.dto';

@Component({
  selector: 'app-p-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss'],
})
export class HomeComponent implements OnInit, OnDestroy {
  ngUnsubscribe = new Subject<void>();

  mainBanner: string[] = [
    'https://www.tncstore.vn/image/catalog/banner/2022/Slide/loi-ich-1640x66-banner160520220.png',
    'https://www.tncstore.vn/image/catalog/Landing%20Page/Pc%20Gaming%2005.2023/banner-build-pc.jpg',
    'https://www.tncstore.vn/image/catalog/banner/2023/Slide/banner--gaming-gear.jpg',
  ];

  subBanner: string[] = [
    'https://www.tncstore.vn/image/catalog/banner/2022/Thang5/laptop-dohoa.png',
    'https://www.tncstore.vn/image/catalog/banner/2022/Thang5/ban-ghe-gaming.png',
    'https://www.tncstore.vn/image/catalog/banner/2022/Thang5/pc-dohoa.png',
    'https://www.tncstore.vn/image/catalog/banner/2022/Thang5/laptop-gaming.png',
  ];

  productCategories = [
    {
      subTitle: 'chân thực',
      img: 'assets/images/headphone.png',
      color: '#1A5DC4',
    },
    {
      subTitle: 'thao tác dễ dàng',
      img: 'assets/images/keyboard.png',
      color: '#343332',
    },
    {
      subTitle: 'mỏng nhẹ',
      img: 'assets/images/laptop.png',
      color: '#01F9C9',
    },
    {
      subTitle: 'bền bỉ',
      img: 'assets/images/modem.png',
      color: '#FFCC3A',
    },
    {
      subTitle: 'sang trọng',
      img: 'assets/images/phone.png',
      color: '#D12137',
    },
    {
      subTitle: 'sống động',
      img: 'assets/images/ipad.png',
      color: '#FF9005',
    },
    {
      subTitle: 'tiện lợi',
      img: 'assets/images/watch.png',
      color: '#FDF292',
    },
    {
      subTitle: 'ảnh sắc nét',
      img: 'assets/images/tv.png',
      color: '#343D57',
    },
  ];

  brandSlider = [
    'https://www.tncstore.vn/image/cache/catalog/logo/akko-logo-228x228.jpg',
    'https://www.tncstore.vn/image/cache/catalog/vga/AFOX/afox-228x228.jpg',
    'https://www.tncstore.vn/image/cache/catalog/brands/lrg_aerocool-228x228.png',
    'https://www.tncstore.vn/image/cache/catalog/brands/ada-228x228.png',
    'https://www.tncstore.vn/image/cache/catalog/brands/lrg_acer-228x228.png',
    'https://www.tncstore.vn/image/cache/catalog/logo new/logo-amd-228x228.jpg',
    'https://www.tncstore.vn/image/cache/catalog/logo new/logo-antec-228x228.jpg',
  ];

  sliderProducts: any[] = [];

  constructor(
    private layoutAPIService: LayoutAPIService,
    @SkipSelf() private productService: ProductService,
    @SkipSelf() private categoryService: CategoryService
  ) {}

  ngOnInit() {
    // this.getProducts();
    this.getProducts();
    this.getCategories();
  }

  getProducts() {
    this.productService
      .getData(1, 15)
      .pipe(takeUntil(this.ngUnsubscribe))
      .subscribe((res: DTOResponse) => {
        this.sliderProducts = res.Data;
      });
  }

  // getListProduct() {
  //   const param: DTOProductFilter = {
  //     Page: 1,
  //     PageSize: 15,
  //   }
  //   this.productService.getProduct(param).pipe(
  //     concatMap((res) => {
  //       if (res.Code === 200) {
  //         res.Data.forEach((product) => {
  //           this.getProductImage(product.Image).pipe(
  //             takeUntil(this.ngUnsubscribe),
  //             tap((imgSrc) => {
  //               product.imageSrc = imgSrc;
  //             })
  //           )
  //         })
  //       }
  //       this.sliderProducts = [...res.Data];
  //       return 
  //     }),
  //     takeUntil(this.ngUnsubscribe)
  //   ).subscribe()
  // }

  getProductImage(imageName: string) {
    return this.productService.getProductImage(imageName);
  }

  getCategories() {
    this.categoryService
      .getData(1, 20)
      .pipe(takeUntil(this.ngUnsubscribe))
      .subscribe((res) => {
        for (let i = 0; i < res.Data.length; i++) {
          this.productCategories[i]['CategoryName'] =
            res.Data[i]['CategoryName'];
        }
      });
  }

  ngOnDestroy(): void {}
}
