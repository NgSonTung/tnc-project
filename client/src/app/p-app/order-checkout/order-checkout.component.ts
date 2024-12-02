import { Component, OnDestroy, OnInit } from '@angular/core';
import { RegisterService } from '../p-layout/shared/services/register.service';
import { Subject, takeUntil } from 'rxjs';
import { Router } from '@angular/router';

@Component({
  selector: 'app-order-checkout',
  templateUrl: './order-checkout.component.html',
  styleUrls: ['./order-checkout.component.scss'],
})
export class OrderCheckoutComponent implements OnInit, OnDestroy {
  isOpenLoginForm: boolean = false;
  ngUnsubscribe = new Subject<void>();

  constructor(private registerService: RegisterService, private router: Router) {}

  ngOnInit(): void {
    this.registerService.registerShown$.pipe(takeUntil(this.ngUnsubscribe)).subscribe(res => {
      this.isOpenLoginForm = res;
      
      if (res) {
        console.log('check');
        
        this.router.navigate['profile'];
      } 
    });
  }

  onOpenLoginForm() {
    this.registerService.openRegisterForm();
  }

  ngOnDestroy(): void {
    this.ngUnsubscribe.next();
    this.ngUnsubscribe.complete();
  }
}
