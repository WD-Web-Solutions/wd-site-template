import { Component, ChangeDetectionStrategy } from '@angular/core';

import { RouterLink } from '@angular/router';

import { UiCardComponent } from '../../shared/components/ui-card/ui-card.component';

import { SERVICES } from '../../core/data/services.data';

import { SeoService } from '../../core/services/seo.service';

import { HeroVideoComponent } from '../../shared/components/hero-video/hero-video.component';



@Component({

  selector: 'app-home',

  standalone: true,

  imports: [

    RouterLink,

    UiCardComponent,

    HeroVideoComponent

  ],

  templateUrl:

    './home.component.html',

  changeDetection: ChangeDetectionStrategy.OnPush,
  styleUrl:

    './home.component.css'

})
export class HomeComponent {


services = SERVICES.slice(0,3);



constructor(

private seoService: SeoService

)

{


this.seoService.updatePage(

'Your Company Name | Commercial Surface Solutions',

'Professional asphalt, striping, coatings, and commercial property improvement services in Your City, State.'

);


}



}