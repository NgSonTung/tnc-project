import {
  NgModule,
  CUSTOM_ELEMENTS_SCHEMA,
  NO_ERRORS_SCHEMA,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { LayoutDefault } from './layout-default/layout-default.component';
import { LayoutRoutingModule } from './p-layout-routing.module';
import { HeaderComponent } from './components/header/header.component';
import { HorizontalBannerComponent } from './components/banner/banner.component';
import { TitleComponent } from './components/title/title.component';
import { FooterComponent } from './components/footer/footer.component';
import { SliderContainerComponent } from './components/slider-container/slider-container.component';
import { SlickCarouselModule } from 'ngx-slick-carousel';
import { CategoryItemComponent } from './components/category-item/category-item.component';
import { BoxProductModule } from './components/boxProduct/boxProduct.module';
import { MenusModule } from '@progress/kendo-angular-menu';
import { NavigationModule } from '@progress/kendo-angular-navigation';
import { BreadcrumbComponent } from './components/breadcrumb/breadcrumb.component';
import { CartComponent } from './components/cart/cart.component';
import { dropdownFilterComponent } from './components/dropdown-filter/dropdown-filter.component';
import { PercentagePipe } from './shared/pipe/percentage.pipe';
import { LayoutModule } from '@progress/kendo-angular-layout';
import { RegisterComponent } from './components/register/register.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ButtonsModule } from '@progress/kendo-angular-buttons';
import { IconsModule } from '@progress/kendo-angular-icons';
import { VnCurrencyPipe } from './shared/pipe/vn-currency.pipe';
import { NgxPaginationModule } from 'ngx-pagination';
import { SalePricePipe } from './shared/pipe/sale-price.pipe';
import { IndicatorsModule } from '@progress/kendo-angular-indicators';
import { StarRatingModule } from 'angular-star-rating';

@NgModule({
  declarations: [
    LayoutDefault,
    HeaderComponent,
    TitleComponent,
    HorizontalBannerComponent,
    FooterComponent,
    SliderContainerComponent,
    CategoryItemComponent,
    BreadcrumbComponent,
    CartComponent,
    dropdownFilterComponent,
    PercentagePipe,
    CartComponent,
    RegisterComponent,
    SalePricePipe,
    VnCurrencyPipe,
  ],
  imports: [
    CommonModule,
    LayoutRoutingModule,
    SlickCarouselModule,
    BoxProductModule,
    MenusModule,
    NavigationModule,
    LayoutModule,
    FormsModule,
    ReactiveFormsModule,
    ButtonsModule,
    IconsModule,
    NgxPaginationModule,
    IndicatorsModule,
    StarRatingModule.forRoot(),
  ],
  schemas: [CUSTOM_ELEMENTS_SCHEMA, NO_ERRORS_SCHEMA],
  exports: [
    VnCurrencyPipe,
    LayoutDefault,
    HeaderComponent,
    TitleComponent,
    HorizontalBannerComponent,
    FooterComponent,
    SlickCarouselModule,
    SliderContainerComponent,
    CategoryItemComponent,
    BreadcrumbComponent,
    dropdownFilterComponent,
    PercentagePipe,
    SalePricePipe,
    CartComponent,
    RegisterComponent,
    VnCurrencyPipe
  ],
})
export class PLayoutModule {}
