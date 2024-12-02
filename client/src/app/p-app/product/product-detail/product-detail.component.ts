import { Component, OnDestroy, OnInit, SkipSelf } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Subject, concatMap, of, pluck, switchMap, takeUntil } from 'rxjs';
import { LayoutAPIService } from '../../p-layout/shared/services/layout-api.service';
import { ProductService } from '../../p-layout/shared/services/product.service';
import { NotificationPopupService } from '../../p-layout/shared/services/notification.service';
import { subImgService } from '../../p-layout/shared/services/subimg.service';
import { Ps_UtilObjectService } from 'src/app/p-lib/ultilities/ulity.object';
import { convertBase64ToImg } from '../../p-layout/shared/core/convertBase64Img';
import { DTOProduct } from '../shared/dto/DTOProduct.dto';
import { RatingService } from '../../p-layout/shared/services/rating.service';
import { StorageService } from '../../p-layout/shared/services/storage.service';
import { OrderService } from '../../p-layout/shared/services/order.service';
import { CategoryService } from '../../p-layout/shared/services/category.service';
import { CartService } from '../../p-layout/shared/services/cart.service';

const PolicyData = [
  {
    text: 'Hỗ trợ trả góp 0%, trả trước 0đ',
    iconName: 'icon_payment.svg',
  },
  {
    text: 'Hoàn tiền 200% nếu có hàng giả',
    iconName: 'icon_money.svg',
  },
  {
    text: 'Giao hàng nhanh trên toàn quốc',
    iconName: 'icon_shipping.svg',
  },
  {
    text: 'Hỗ trợ kĩ thuật online 7/7',
    iconName: 'icon_chat.svg',
  },
];

@Component({
  selector: 'app-product-detail',
  templateUrl: './product-detail.component.html',
  styleUrls: ['./product-detail.component.scss'],
})
export class ProductDetailComponent implements OnInit, OnDestroy {
  private unsubscription$ = new Subject<void>();

  productDetail: DTOProduct = new DTOProduct();
  productName: string = '';
  saleprice: number = 0;
  rating = 0;
  breadCrumbList: string[] = [];
  policyList: any[] = PolicyData;
  subImgList: string[] = [];

  //Cart handle declarations
  cartQuantity: number = 1;

  //subscription
  ngUnsubscribe = new Subject<void>();

  constructor(
    private route: ActivatedRoute,
    private productAPIService: ProductService,
    private storageService: StorageService,
    private notiService: NotificationPopupService,
    private subImgService: subImgService,
    @SkipSelf() private ratingService: RatingService,
    @SkipSelf() private orderService: OrderService,
    @SkipSelf() private cartService: CartService,
    @SkipSelf() private productService: ProductService
  ) {}

  ngOnInit(): void {
    this.GetDetailProduct();
  }

  buyNow() {
    const orderID = this.storageService.getOrders().orderId;
    const productID = this.productDetail.ProductID;
    const userID = this.storageService.getUser().UserID;

    //logged in
    if (userID) {
      this.orderService.getData(1, 20, `?UserID=${userID}`).subscribe((res) => {
        const product = res.Data.DataInOrder.find(
          (product) => product.ProductID == productID
        );
        if (product) {
          const body = {
            ProductID: productID,
            Amount: product.Amount + this.cartQuantity,
            OrderID: orderID,
          };
          product.Amount + this.cartQuantity <= product.Stock
            ? this.orderService
                .updateCart(body)
                .pipe(takeUntil(this.unsubscription$))
                .subscribe((res) => {
                  this.orderService
                    .getData(1, 20, `?UserID=${userID}`)
                    .pipe(takeUntil(this.ngUnsubscribe))
                    .subscribe((res: any) => {
                      this.storageService.saveOrders(res.Data);
                      this.cartService.onToggleCartPopUpState(true);
                    });
                })
            : this.notiService.onError(
                'Số lượng sản phẩm vượt quá số lượng tồn!'
              );
        } else {
          const body = {
            ProductID: productID,
            Amount: this.cartQuantity,
            OrderID: orderID,
          };
          this.orderService
            .addToCart(body)
            .pipe(takeUntil(this.unsubscription$))
            .subscribe((res) => {
              this.orderService
                .getData(1, 20, `?UserID=${userID}`)
                .pipe(takeUntil(this.ngUnsubscribe))
                .subscribe((res: any) => {
                  this.storageService.saveOrders(res.Data);
                  this.cartService.onToggleCartPopUpState(true);
                });
            });
        }
      });
    } else {
      let product = this.storageService
        .getOrders()
        .orders.find((product) => product.ProductID == productID);

      if (product) {
        let orders = this.storageService.getOrders();
        product.Amount += this.cartQuantity;
        orders.totalAmount += this.cartQuantity;
        if (product.Amount <= product.Stock) {
          for (let i = 0; i < orders.orders.length; i++) {
            if (orders.orders[i].ProductID === product.ProductID) {
              orders.orders[i] = product;
              break;
            }
          }
          this.storageService.saveOrders2(orders);
          this.cartService.onToggleCartPopUpState(true);
        } else {
          this.notiService.onError('Số lượng sản phẩm vượt quá số lượng tồn!');
        }
      } else {
        let orders = this.storageService.getOrders();
        this.productService
          .getDataById(this.productDetail.ProductID)
          .subscribe((res) => {
            let newProduct = res.Data;
            newProduct.Amount = this.cartQuantity;
            orders.orders.push(newProduct);
            orders.totalAmount += this.cartQuantity;
            this.storageService.saveOrders2(orders);
            this.cartService.onToggleCartPopUpState(true);
          });
      }
    }
  }

  addToCart() {
    const orderID = this.storageService.getOrders().orderId;
    const productID = this.productDetail.ProductID;
    const userID = this.storageService.getUser().UserID;

    if (userID) {
      this.orderService.getData(1, 20, `?UserID=${userID}`).subscribe((res) => {
        const product = res.Data.DataInOrder.find(
          (product) => product.ProductID == productID
        );
        if (product) {
          const body = {
            ProductID: productID,
            Amount: product.Amount + this.cartQuantity,
            OrderID: orderID,
          };
          product.Amount + this.cartQuantity <= product.Stock
            ? this.orderService
                .updateCart(body)
                .pipe(takeUntil(this.unsubscription$))
                .subscribe((res) => {
                  this.notiService.onSuccess('Thêm vào giỏ hàng thành công!');
                  window.location.reload();
                })
            : this.notiService.onError(
                'Số lượng sản phẩm vượt quá số lượng tồn!'
              );
        } else {
          const body = {
            ProductID: productID,
            Amount: this.cartQuantity,
            OrderID: orderID,
          };
          this.orderService
            .addToCart(body)
            .pipe(takeUntil(this.unsubscription$))
            .subscribe((res) => {
              this.notiService.onSuccess('Thêm vào giỏ hàng thành công!');
              window.location.reload();
            });
        }
      });
    } else {
      let product = this.storageService
        .getOrders()
        .orders.find((product) => product.ProductID == productID);

      if (product) {
        let orders = this.storageService.getOrders();
        product.Amount += this.cartQuantity;
        orders.totalAmount += this.cartQuantity;
        if (product.Amount <= product.Stock) {
          for (let i = 0; i < orders.orders.length; i++) {
            if (orders.orders[i].ProductID === product.ProductID) {
              orders.orders[i] = product;
              break;
            }
          }
          this.storageService.saveOrders2(orders);
          this.notiService.onSuccess('Thêm vào giỏ hàng thành công!');
          window.location.reload();
        } else {
          this.notiService.onError('Số lượng sản phẩm vượt quá số lượng tồn!');
        }
      } else {
        let orders = this.storageService.getOrders();
        this.productService
          .getDataById(this.productDetail.ProductID)
          .subscribe((res) => {
            let newProduct = res.Data;
            newProduct.Amount = this.cartQuantity;
            orders.orders.push(newProduct);
            orders.totalAmount += this.cartQuantity;
            this.storageService.saveOrders2(orders);
            this.notiService.onSuccess('Thêm vào giỏ hàng thành công!');
            window.location.reload();
          });
      }
    }
  }

  updateRating(ProductID) {
    this.ratingService
      .getDataById(ProductID)
      .pipe(takeUntil(this.unsubscription$))
      .subscribe((res) => {
        let total_ratings =
          res.Data._5star +
          res.Data._4star +
          res.Data._3star +
          res.Data._2star +
          res.Data._1star;
        let stars =
          5 * res.Data._5star +
          4 * res.Data._4star +
          3 * res.Data._3star +
          2 * res.Data._2star +
          1 * res.Data._1star;
        const average_rating = stars / total_ratings;
        this.rating = average_rating;
      });
  }

  GetDetailProduct() {
    this.route.params
      .pipe(
        pluck('productname'),
        switchMap((params) => {
          this.productName = params;
          return this.productAPIService.getDetaiProductByName(this.productName);
        }),
        concatMap((res) => {
          if (res.Code === 200) {
            this.productDetail = { ...res.Data[0] };
            this.updateRating(this.productDetail.ProductID);
            return this.subImgService.getProductSubImage(
              this.productDetail.ProductID
            );
          } else {
            this.notiService.onError(
              'Đã xảy ra lỗi khi load chi tiết sản phẩm'
            );
            return of();
          }
        }),
        takeUntil(this.ngUnsubscribe)
      )
      .subscribe((res: any) => {
        if (Ps_UtilObjectService.hasListValue(res.Data)) {
          const imgList = [...res.Data];
          const mainImg = convertBase64ToImg(this.productDetail.Base64Image);
          this.subImgList.unshift(mainImg);
          imgList.forEach((img) => {
            const convertedImg = convertBase64ToImg(img.base64);
            this.subImgList.push(convertedImg);
          });
        } else {
          this.notiService.onError('Đã xảy ra lỗi khi load ảnh sản phẩm');
        }
      });
  }

  onHandleQuantity(type: string) {
    if (type === 'increase') {
      this.cartQuantity + 1 <= this.productDetail.Stock &&
        (this.cartQuantity += 1);
    } else {
      if (this.cartQuantity > 1) {
        this.cartQuantity -= 1;
      }
    }
  }

  onRatingProduct(event: any) {
    const rating = event.rating;
    let updateRating = { ProductID: this.productDetail.ProductID };
    this.ratingService
      .getDataById(this.productDetail.ProductID)
      .pipe(takeUntil(this.unsubscription$))
      .subscribe((res) => {
        updateRating[`_${rating}star`] = res.Data[`_${rating}star`];
        updateRating[`_${rating}star`] += 1;
        this.ratingService
          .addRating(updateRating)
          .pipe(takeUntil(this.unsubscription$))
          .subscribe((res) => {
            this.updateRating(this.productDetail.ProductID);
            this.notiService.onSuccess('Đánh giá thành công!');
          });
      });
  }

  ngOnDestroy(): void {
    this.ngUnsubscribe.next();
    this.ngUnsubscribe.complete();
  }
}
