import { DTOCategory } from './../../shared/dto/DTOCategory';
import { RegisterService } from './../../shared/services/register.service';
import {
  Component,
  ElementRef,
  HostListener,
  Input,
  OnDestroy,
  OnInit,
  SkipSelf,
  TemplateRef,
  ViewChild,
} from '@angular/core';
import {
  Subject,
  Subscription,
  debounce,
  debounceTime,
  delay,
  switchMap,
  take,
  takeUntil,
} from 'rxjs';
import { LayoutAPIService } from '../../shared/services/layout-api.service';
import { Ps_UtilObjectService } from 'src/app/p-lib/ultilities/ulity.object';
import { CartService } from '../../shared/services/cart.service';
import { AuthService } from 'src/app/p-app/http-interceptors/auth.service';
import { DTOUser } from 'src/app/p-app/_models/DTOUser';
import { StorageService } from '../../shared/services/storage.service';
import { NavigationExtras, Route, Router } from '@angular/router';
import { NotificationPopupService } from '../../shared/services/notification.service';
import { CategoryService } from '../../shared/services/category.service';
import { OrderService } from '../../shared/services/order.service';
import { DTOResponse } from '../../shared/dto/DTOResponse';
import { FormControl } from '@angular/forms';
import { ProductService } from '../../shared/services/product.service';
import { DTOProduct } from '../../shared/dto/DTOProduct';

@Component({
  selector: 'app-p-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss'],
})
export class HeaderComponent implements OnInit, OnDestroy {
  @ViewChild('searchContainer') containerRef!: ElementRef;
  userMenu: any[] = [
    { text: 'TNCMember', icon: 'k-i-user' },
    { text: 'Đăng xuất', icon: 'k-i-home' },
  ];

  constructor(
    private layoutAPIService: LayoutAPIService,
    private authService: AuthService,
    private storageService: StorageService,
    private route: Router,
    private notificationService: NotificationPopupService,
    @SkipSelf() private cartService: CartService,
    @SkipSelf() private categoryService: CategoryService,
    @SkipSelf() private registerService: RegisterService,
    @SkipSelf() private orderService: OrderService,
    @SkipSelf() private productService: ProductService
  ) {}
  userName: string = '';
  ngUnsubscribe = new Subject<void>();
  isLoggedIn: boolean = false;
  searchInputValue = new FormControl('');
  searchedProductList: DTOProduct[] = [];

  ngOnInit(): void {
    this.getOrders();
    this.authService._isLoggedIn
      .pipe(takeUntil(this.ngUnsubscribe))
      .subscribe((res) => {
        this.isLoggedIn = res;
        // console.log(this.isLoggedIn);
        if (this.isLoggedIn) {
          this.userName = this.storageService.getUser().UserName;
        }
      });
    this.getCategoryList();

    this.searchInputValue.valueChanges
      .pipe(
        debounceTime(1000),
        switchMap((res) => this.productService.getDetaiProductByName(res)),
        takeUntil(this.ngUnsubscribe)
      )
      .subscribe(
        (res) => {
          if (res.Code === 200 && Ps_UtilObjectService.hasListValue(res.Data)) {
            this.searchedProductList = [...res.Data];
            this.searchInputValue.patchValue('', { emitEvent: false }); //prevent emit when reset value of input
            console.log(this.searchedProductList);
          }
        },
        (error) => {
          console.error('Error:', error);
        }
      );
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent) {
    if (!this.containerRef?.nativeElement.contains(event.target)) {
      this.searchedProductList = [];
    }
  }

  navigateDetail(productName: string) {
    this.searchedProductList = [];
    this.route.navigate(['/product', productName]);
  }

  //Category list declaration
  headerMenuItems: any[] = [
    {
      text: 'DANH MỤC SẢN PHẨM',
      icon: 'icon_computer.svg',
      path: '',
      items: [],
    },
    {
      text: 'XÂY DỰNG CẤU HÌNH',
      icon: 'icon_setting.svg',
      path: 'building',
      items: [],
    },
  ];
  cartItems: number = 0;
  //Subscription

  toggleCart = () => {
    const newValue = !this.cartService.isCartPopUpOpened.value;
    this.cartService.onToggleCartPopUpState(newValue);
  };

  toggleRegister(): void {
    this.registerService.toggleRegisterShown();
  }

  getOrders() {
    const userId = this.storageService.getUser().UserID;
    if (!userId) {
      const orders = this.storageService.getOrders();
      if (!orders) {
        const orders = { TotalAmount: 0, DataInOrder: [], OrderID: -1 };
        this.storageService.saveOrders(orders);
        this.cartItems = this.storageService.getOrders().totalAmount;
      } else {
        this.cartItems = orders.totalAmount;
      }
    } else {
      this.orderService
        .getData(1, 20, `?UserID=${userId}`)
        .pipe(takeUntil(this.ngUnsubscribe))
        .subscribe((res: DTOResponse) => {
          console.log(res);

          this.storageService.saveOrders(res.Data);
          this.cartItems = res.Data.TotalAmount > 0 ? res.Data.TotalAmount : 0;
        });
    }
  }

  getCategoryList() {
    this.categoryService
      .getData(1, 100)
      .pipe(takeUntil(this.ngUnsubscribe))
      .subscribe((res) => {
        const categories = res.Data;
        // if (Ps_UtilObjectService.hasListValue(categories)) {
        categories.forEach((item: DTOCategory) => {
          this.headerMenuItems[0].items.push({
            text: item.CategoryName,
            path: `${item.CategoryName}`,
          });
        });
        // } else {
        //   window.alert('Không load được danh sách Category');
        // }
      });
  }

  onHandleMenu(type: string) {
    if (type === 'TNCMember') {
      this.route.navigate(['/profile']);
    } else if (type === 'Đăng xuất') {
      this.authService.logout().subscribe(() => {
        this.authService.setLoginState(false);
        this.storageService.clean();
        this.userName = '';
        this.notificationService.onSuccess('Đăng xuất thành công');
        window.location.reload();
        this.route.navigate(['']);
      });
    }
  }

  onCheckoutOrder() {
    if (this.isLoggedIn) {
      this.route.navigate(['profile']);
    } else {
      this.route.navigate(['orderCheckout']);
    }
  }

  onNavigate(path: string) {
    console.log(path);
    this.route.navigate([`/${path}`]);
  }

  ngOnDestroy(): void {
    this.ngUnsubscribe.next();
    this.ngUnsubscribe.complete();
  }
}
