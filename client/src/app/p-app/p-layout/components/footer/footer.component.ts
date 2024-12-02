import { Component, OnDestroy, OnInit } from '@angular/core';
import { LayoutAPIService } from '../../shared/services/layout-api.service';
import { DTOBrand } from '../../shared/dto/DTOBrand';
import { Subscription } from 'rxjs';
import { Ps_UtilObjectService } from 'src/app/p-lib/ultilities/ulity.object';
import { DTOCategory } from '../../shared/dto/DTOCategory';

@Component({
  selector: 'app-footer',
  templateUrl: './footer.component.html',
  styleUrls: ['./footer.component.scss'],
})
export class FooterComponent implements OnInit, OnDestroy {
  //Declare variables
  categoryList: DTOCategory[] = [];
  generalInfo: string[] = [
    'Giới thiệu TNC Store',
    'Tuyển dụng',
    'Tin tức',
    'Ý kiến khách hàng',
    'Liên hệ hợp tác',
  ];
  genralPolicy: string[] = [
    'Quy định chung',
    'Chính sách vận chuyển',
    'Chính sách bảo hành',
    'Chính sách đổi, trả lại hàng',
    'Chính sách cho doanh nghiệp',
  ];
  promotionInfo: string[] = [
    'Sản phẩm bán chạy',
    'Sản phẩm khuyến mãi',
    'Hàng thanh lý',
  ];
  socialIcons: string[] = [
    'https://www.tncstore.vn/catalog/view/theme/default/image/facebook.png',
    'https://www.tncstore.vn/catalog/view/theme/default/image/youtube.png',
    'https://www.tncstore.vn/catalog/view/theme/default/image/shoppe.png',
    'https://www.tncstore.vn/catalog/view/theme/default/image/instagram.png',
  ];

  //Subscription
  getCategoryList_sst: Subscription;

  constructor(private readonly layoutAPIService: LayoutAPIService) {}

  ngOnInit(): void {
    this.getCategoryList();
  }

  getCategoryList() {
    this.getCategoryList_sst = this.layoutAPIService
      .GetCategories()
      .subscribe((res: any) => {
        if (Ps_UtilObjectService.hasValue(res) && res.code == 200) {
          this.categoryList = [...res.data.categories];
          console.log(this.categoryList);
        }
      });
  }

  ngOnDestroy(): void {
    this.getCategoryList_sst?.unsubscribe();
  }
}
