import { Component, ChangeDetectionStrategy } from '@angular/core';

import { RouterOutlet } from '@angular/router';

import { NavbarComponent } from './navbar/navbar.component';

import { FooterComponent } from './footer/footer.component';


@Component({

  selector: 'app-public-layout',

  standalone: true,

  imports: [

    RouterOutlet,

    NavbarComponent,

    FooterComponent

  ],

  templateUrl:
    './public-layout.component.html',

  changeDetection: ChangeDetectionStrategy.OnPush,
  styleUrl:
    './public-layout.component.css'

})
export class PublicLayoutComponent {


}