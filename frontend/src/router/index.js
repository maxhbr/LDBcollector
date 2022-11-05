import Vue from 'vue'
import Router from 'vue-router'
// import main from '@/pages/main'
// import search from '@/pages/search'
// import { component } from 'vue/types/umd'
// import result from '@/pages/result'
// import hp from '@/pages/Homepage'

Vue.use(Router)

export default new Router({
  routes: [
    {
    path: '/',
    name: 'index',
    // component: main, 
    components : {first: ()=> import('@/pages/main')}
  },
  {
    path: '/search',
    name: 'search',
    components : {first: ()=> import('@/pages/search')},
    children: [
      {
        path: '/search/questions',
        components: {second: ()=> import('@/components/questions')}
      }
    ]
  },
  // {
  //   path: '/result',
  //   name: 'result',
  //   component: result,
  // },
  
]
})
