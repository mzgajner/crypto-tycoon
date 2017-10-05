<template>
  <div id="app" v-if="grid.length>0">
   <div class="row" v-for="row in grid">
     <div  v-for="column in row" :class="'column' + ' ' + column.type">

     </div>
   </div>
  </div>
</template>

<script>
export default {
  name: 'app',
  data () {
    return {
      grid: []
    }
  },
  created () {
    for(var r=0; r<18; r++) {
        for(var c=0; c<27; c++) {
            if(!this.grid[r]) {
                this.grid[r] = [];
            }
            this.grid[r][c] = {
                type: r%3==1 || c%3==1 ? 'road' : 'land'
            }
        }
    }
  }
}
</script>

<style lang="scss">
  .row {
    display:flex;
  }
  .column {
    width:40px;
    height:40px;
    &.land {
      background-color: darkgreen;
    }
    &.road {
      background-color: dimgrey;
    }
  }

</style>
