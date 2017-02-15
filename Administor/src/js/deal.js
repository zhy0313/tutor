(function(){
  Vue.http.interceptors.push(function(request, next){
    request.credentials = true;
    next();
  });
	var vm = new Vue({
      el: 'body',
      data: {
        timer: null,
        domain: 'http://www.yinzishao.cn:8000',
        status:{
  	  	  isSelecting: true,
          isLoading: false,
          isUploadImg: false,
          selected: '',
          isSend: '',
          isGreen: true,
          isFeeInfo: false,
          isFeeInfoTrue: false,
          isList: true,
          isNoList: false,
      	},
      	mainData:[
          // {oa_id: 0,tea:2,pd_name: '张小可',name:'王小源',result: '已处理',isDeal: false,screenshot_path:'../img/user02.png'},
          // {oa_id: 1,tea:3,pd_name: '张可',name:'王小源',result: '未处理',isDeal: true,screenshot_path:'../img/user02.png'},
          // {oa_id: 2,tea:4,pd_name: '张大可',name:'王小源',result: '未处理',isDeal: true,screenshot_path:'../img/user02.png'},
        ],
        detailedList: [],
        jsonData: [],
        para: {
          'size':15,
          'start':0
        },
        // form: {
        //   fee: Number,
        // }
      },
      ready: function(){
      	this.render();
        this.status.isLoading = true;
      },
      methods: {
        down: function(){
          this.form.size = 5;
          this.para.start++;
          if(this.jsonData.length!==0){
            this.render();
          }
        },
      	render: function(){
          var self = this;
           this.$http.post(this.domain+'/getDoneList',this.para,{
               crossOrigin: true,
               headers:{
                  'Content-Type':'application/json' 
               }
           }).then(function(res){
            console.log(res.json());
            if(res.json().success == 0){
              console.log(res.json().error);
            }else{
              this.jsonData = res.json();
              var data = res.json();
              if(data.length!=0){
                for(var i =0;i<data.length;i++){
                  data[i].screenshot_path = this.domain+data[i].screenshot_path;
                }
                var json=self.mainData.concat(data);
                this.$set('mainData',json);
              }else{
                if(this.mainData.length==0){
                  this.status.isList = false;
                  this.status.isNoList = true;
                }
              }
            }
           }) 
      	},
        onUser:function(){
          window.location.href = './userAdministor.html';
        },
        onDeal: function(){
          this.status.isUploadImg = false;
        },
        onOther: function(){
          window.location.href = './other.html';
        },
        onDeal: function(index){
          this.status.selected = index;
          var self =this;
          // if(this.mainData[index].info == '未定价'){
          //   this.status.isFeeInfo = true;
          // }else if(this.mainData[index].info == '已定价'){
          //   this.status.isFeeInfoTrue = true;
          //   this.timer && clearTimeout(this.timer);
          //   this.timer = setTimeout(function(){
          //     self.status.isFeeInfoTrue = false;
          //   }, 2000);
          // }else{
            this.status.isUploadImg = true;
            this.detailedList = this.mainData[index];
            if(this.mainData[index].result == '未处理'){
              this.status.isSend = '发送联系方式';
              this.status.isGreen = true;
            }else{
              this.status.isSend = '已发送';
              this.status.isGreen = false;
            }
          // }
        },
        onClose: function(){
        	this.status.isUploadImg = false;
        },
        onSubmitMsg: function(index){
          var list = this.mainData[index];
        	if(this.status.isSend == '发送联系方式'){
        		this.$http.post(this.domain+'/sendPhone',{
              "tea_id":list.tea,
              "oa_id":list.oa_id,
              "tel":1881234567
            },{
              crossOrigin:true,
              headers:{
                'Content-Type':'application/json; charset=UTF-8' 
              }

            }).then(function(res){
              if(res.json().success == 1){
                var self = this;
              	this.status.isSend = '已发送';
              	list.isDeal = false;
                this.timer && clearTimeout(this.timer);
                this.timer = setTimeout(function(){
                  list.result = '已处理';
                  self.status.isUploadImg = false;
                }, 2000); 
              }
            })
        	}else {
        		return false;
        	}
        },
      }
	});
})()