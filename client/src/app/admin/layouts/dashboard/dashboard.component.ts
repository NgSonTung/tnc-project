import { Component, OnInit } from '@angular/core';
import { Subject } from 'rxjs';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss'],
})
export class DashboardComponent implements OnInit {
  navShown: boolean = true;
  subTableShown: boolean = false;
  ngUnsubscription$ = new Subject<void>();

  constructor() {}

  ngOnInit(): void {

  }

  toggleNav = () => {
    this.navShown = !this.navShown;
  };

  toggleSubTable = () => {
    this.subTableShown = !this.subTableShown;
  };
}
