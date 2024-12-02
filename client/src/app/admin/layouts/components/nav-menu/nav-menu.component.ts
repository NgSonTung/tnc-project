import { Component } from '@angular/core';

@Component({
  selector: 'app-nav-menu',
  templateUrl: './nav-menu.component.html',
  styleUrls: ['./nav-menu.component.scss'],
})
export class NavMenuComponent {
  navItems = [
    { src: 'assets/icon/home-line.svg' },
    { src: 'assets/icon/bar-chart-square-02.svg' },
    { src: 'assets/icon/layers-three-01.svg' },
    { src: 'assets/icon/check-done-01.svg' },
    { src: 'assets/icon/pie-chart-03.svg' },
    { src: 'assets/icon/users-01.svg' },
  ];

  selectedIndex: number = 0;

  setSelectedIndex(id: number) {
    this.selectedIndex = id;
  }
}
