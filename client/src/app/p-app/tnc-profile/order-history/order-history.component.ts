import { Component, OnInit } from '@angular/core';
import { Subject, concatMap, forkJoin, switchMap, takeUntil } from 'rxjs';
import { DTOOrder } from '../share/DTO/orderDTO.dto';
import { OrderService } from '../../p-layout/shared/services/order.service';
import { StorageService } from '../../p-layout/shared/services/storage.service';
import { DTOProduct } from '../../p-layout/shared/dto/DTOProduct';
import { Ps_UtilObjectService } from 'src/app/p-lib/ultilities/ulity.object';
import { LayoutAPIService } from '../../p-layout/shared/services/layout-api.service';
import { NotificationPopupService } from '../../p-layout/shared/services/notification.service';
import { ProductService } from '../../p-layout/shared/services/product.service';
@Component({
  selector: 'app-order-history',
  templateUrl: './order-history.component.html',
  styleUrls: ['./order-history.component.scss'],
})
export class OrderHistoryComponent implements OnInit {
  //Grid view
  orderGridView: Subject<any> = new Subject<any>();
  range = { start: null, end: null };
  ngUnsubscribe$ = new Subject<void>();
  userID: number = null;
  constructor(
    private orderService: OrderService,
    private storageService: StorageService,
    private notiService: NotificationPopupService,
    private productAPIService: ProductService,
    private notificationService: NotificationPopupService
  ) {}
  fullName: String = 'NAME';
  orderDetailProductList = [];
  isDetailProductPopupOpened: boolean = false;
  isCanceled: boolean = false;
  orderTotal: number = 0;
  totalPay: number = 0;
  selectedOrderForCancellation: any;
  ngOnInit(): void {
    this.userID = this.storageService.getUser().UserID;
    this.getPersonalOrders();
    const userData = this.storageService.getUser();
    userData.FullName && (this.fullName = userData.FullName);
  }

  deleteOrder(id: number): void {
    this.orderService.cancelOrder(id).subscribe((res) => {
      this.notificationService.onSuccess('Xóa đơn hàng thành công!');
    });
    this.getPersonalOrders();
  }

  getPersonalOrders() {
    this.orderService
      .getDataById(this.userID)
      .pipe(takeUntil(this.ngUnsubscribe$))
      .subscribe((res) => {
        if (res.Code === 200) {
          this.orderTotal = res.Data.TotalOrder;
          this.orderGridView.next({
            data: res.Data.Data,
            total: res.Data.TotalOrder,
          });
          let paid = 0;
          res.Data.Data.forEach((order) => {
            order.StatusID == 2 && (paid += order.TotalPrice);
          });
          this.totalPay = paid;
          console.log(this.totalPay);
        }
      });
  }

  getOrderDetail(orderID: number) {
    this.orderService
      .getOrderDetail(orderID, this.userID)
      .pipe(
        takeUntil(this.ngUnsubscribe$),
        switchMap((res) => {
          if (Ps_UtilObjectService.hasListValue(res.Data)) {
            this.orderDetailProductList = [...res.Data];
            console.log(this.orderDetailProductList);

            // Create an array of observables to fetch product details by name
            const observables = this.orderDetailProductList.map((product) =>
              this.productAPIService.getProductImage(product.Image)
            );

            // Combine observables using forkJoin to get all responses together
            return forkJoin(observables);
          } else {
            this.notiService.onError('Lỗi khi tìm sản phẩm');
            return [];
          }
        })
      )
      .subscribe(
        (responses) => {
          // Assuming the response structure matches your expectations
          this.orderDetailProductList.forEach((product, index) => {
            console.log(responses);
            product.ImgSrc = responses[index]?.Data.Base64 || ''; // Update ImgSrc
          });
          console.log(this.orderDetailProductList);
        },
        (error) => {
          console.error('Error:', error);
        }
      );
    this.toggleProductPopup(true);
  }

  toggleProductPopup(value: boolean) {
    this.isDetailProductPopupOpened = value;
  }

  public close(status: string, orderid: any): void {
    console.log(`Dialog result: ${status}`);
    if ((status = 'yes')) {
      this.deleteOrder(orderid);
    }
    this.isCanceled = false;
  }

  public open(): void {
    this.isCanceled = true;
  }
}
