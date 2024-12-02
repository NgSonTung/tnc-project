import {
  Component,
  ViewChild,
  ElementRef,
  Renderer2,
  Output,
  EventEmitter,
} from '@angular/core';

@Component({
  selector: 'app-minimized-bar',
  templateUrl: './minimized-bar.component.html',
  styleUrls: ['./minimized-bar.component.scss'],
})
export class MinimizedBarComponent {
  constructor(private renderer: Renderer2) {}
  @Output() showChat = new EventEmitter<void>();

  @ViewChild('draggableDiv', { static: true }) draggableDiv!: ElementRef;
  active: boolean = false;
  isDragging = false;
  initialX: number = 0;
  initialY: number = 0;
  offsetX = 0;
  offsetY = 0;

  toggleActive() {
    this.active = !this.active;
  }

  onShowChat() {
    this.showChat.emit();
  }

  onMouseDown(event: MouseEvent) {
    this.isDragging = true;
    this.renderer.setStyle(
      this.draggableDiv.nativeElement,
      'transition',
      `none`
    );
    this.initialX = event.clientX - this.offsetX;
    this.initialY = event.clientY - this.offsetY;
  }

  onMouseMove(event: MouseEvent) {
    if (this.isDragging) {
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;
      event.preventDefault();
      this.offsetX = event.clientX - this.initialX;
      this.offsetY = event.clientY - this.initialY;
      this.offsetX = Math.max(
        0,
        Math.min(
          this.offsetX,
          viewportWidth - this.draggableDiv.nativeElement.offsetWidth
        )
      );
      this.offsetY = Math.max(
        0,
        Math.min(
          this.offsetY,
          viewportHeight - this.draggableDiv.nativeElement.offsetHeight
        )
      );
      this.renderer.setStyle(
        this.draggableDiv.nativeElement,
        'transform',
        `translate(${this.offsetX}px, ${this.offsetY}px)`
      );
    }
  }

  onMouseUp(event: MouseEvent) {
    this.isDragging = false;
    this.renderer.setStyle(
      this.draggableDiv.nativeElement,
      'transition',
      `transform 0.2s ease-in-out`
    );
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    const halfWidth = this.draggableDiv.nativeElement.offsetWidth / 2;
    const halfHeight = this.draggableDiv.nativeElement.offsetHeight / 2;

    let targetX = this.offsetX;
    let targetY = this.offsetY;

    if (targetX < viewportWidth / 2) {
      targetX = 0;
    } else {
      targetX = viewportWidth - this.draggableDiv.nativeElement.offsetWidth;
    }

    if (targetY < viewportHeight / 2) {
      targetY = 0;
    } else {
      targetY = viewportHeight - this.draggableDiv.nativeElement.offsetHeight;
    }

    // Adjust the target position based on the closest edge
    if (Math.abs(targetX - this.offsetX) < Math.abs(targetY - this.offsetY)) {
      targetY = this.offsetY;
    } else {
      targetX = this.offsetX;
    }

    this.renderer.setStyle(
      this.draggableDiv.nativeElement,
      'transform',
      `translate(${targetX}px, ${targetY}px)`
    );
    this.offsetX = targetX;
    this.offsetY = targetY;
  }
}
