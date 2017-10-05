<template>
    <div>
        <button @click="startBuilding">
            Build house
        </button>
        <h1>Crypto balance: {{ money }}</h1>
        <div id="app" v-if="grid.length>0" :class="wrapperClass">
            <div class="row" v-for="(row, row_index) in grid">
                <div
                    v-for="(column, column_index) in row"
                    :class="'column ' + column.type"
                    @click="build(column, row_index, column_index)"
                >
                    <template v-for="object in column.content">
                        <div v-if="object.type === 'person'" class="person" :key="object.id"></div>
                        <div v-else-if="object.type === 'building'" :class="'building ' + object.currency"></div>
                    </template>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import io from 'socket.io-client'

let server = io.connect('http://localhost:5000');


export default {
    name: 'app',
    data () {
        return {
            grid: [],
            building: false,
            money: 0,
            id: null,
        }
    },
    computed: {
        wrapperClass() {
            return this.building ? 'is-building' : '';
        },
        cellsWithContent() {
            let cellsWithContents = [];
            this.grid.forEach(row => {
                row.forEach(column => {
                    if(column.content) {
                        cellsWithContents.push(column);
                    }
                })
            })
            return cellsWithContents;
        }
    },
    methods: {
        startBuilding() {
            this.building = true;
        },
        build(column, x, y) {
            if (column.type !== 'land') return;
            this.building = false;
            let bla = io.connect('http://localhost:5000');
            bla.emit('build', {
                position: [x, y],
                money: this.money,
                player_id: this.id
            });
        }
    },
    created() {
        this.id = Math.floor(Math.random() * 64);
        server.emit('register',{ id: this.id });
        server.on('update', (payload) => {
            console.log('start occured', payload);
            this.grid = payload.world;
            this.money = payload.money[this.id];
        });
    },
}
</script>

<style lang="scss">
    .row {
        display:flex;
    }
    .column {
        width:40px;
        height:40px;
        position: relative;
        &.land {
            background-color: #67cbb1;
        }
        &.road {
            background-color: white;
        }
    }

    .is-building {
        .land:hover {
            background-color: greenyellow;
        }
    }

    .person {
        left: 0px;
        top: 0px;
        height: 40px;
        width: 40px;
        background-size: 40px 40px;
        background-image: url("data:image/svg+xml;base64,PHN2ZyB3aWR0aD0nMjAwJyBoZWlnaHQ9JzIwMCcgZmlsbD0iIzAwMDAwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxuczp4bGluaz0iaHR0cDovL3d3dy53My5vcmcvMTk5OS94bGluayIgdmVyc2lvbj0iMS4xIiB4PSIwcHgiIHk9IjBweCIgdmlld0JveD0iMCAtMjUuMzY2IDEwMCAxMjUuMzY2IiBlbmFibGUtYmFja2dyb3VuZD0ibmV3IDAgLTI1LjM2NiAxMDAgMTI1LjM2NiIgeG1sOnNwYWNlPSJwcmVzZXJ2ZSI+PGNpcmNsZSBjeD0iNjAuNTA2IiBjeT0iLTguNjk2IiByPSIxMC44NDEiLz48cGF0aCBkPSJNOTMuNDEzLDM1LjY0OEw3NS45NzUsMjcuNjNMNjUuMTc2LDkuMTM1QzYzLjA1LDQuNSw1NS45MTcsMy45Miw1MS40NzMsNi41MjhMMzEuNzk3LDE5LjM1ICBjLTAuNzEyLDAuNjc1LTEuMjIsMS41NzctMS4zOTYsMi42MTlsLTMuNDA3LDIwLjEwMmMtMC4xNCwwLjgyMy0wLjA1NSwxLjYzLDAuMjA5LDIuMzYzSDEyLjkxNWMtMS4yOTQsMC0yLjM0MywxLjI4NC0yLjM0MywyLjg2NyAgdjIxLjMzN2MwLDEuNTg1LDEuMDQ5LDIuODY4LDIuMzQzLDIuODY4aDIyLjkwNkwyNS41NzksODQuNTU3Yy00LjY3NSw1Ljk1NywzLjU3OCwxMy4xNDgsOC4yMTgsNy4yMzRsMTMuODI1LTE2LjM0MyAgYzAuNzYtMC45NjksMS4xNjYtMi4xMDMsMS4yMzctMy4yNDZsMi44MzgtMTYuOTdsMTMuMzk4LDM1LjIwMWMyLjcwNSw3LjEwMywxMi42MjksMi44NjQsOS45NTEtNC4xNjhMNjAuODg0LDQ2LjQyOGwzLjI2OC0yMC40NTcgIGw0LjU3Myw3LjgzM2MwLjY5LDEuMTgyLDEuODE3LDEuOTQ3LDMuMDU4LDIuMjE1bDE3LjcxNSw3LjE0NkM5NC45ODYsNDUuNjg1LDk4LjkwNywzOC4xNzIsOTMuNDEzLDM1LjY0OHogTTQxLjYyMyw0NC40MzRoLTUuNTk3ICBsMy4yODItMTguOTMzbDYuMTQ4LTMuOTlMNDEuNjIzLDQ0LjQzNHoiLz48L3N2Zz4=");
        position: absolute;
        transition: all 0.5s linear;
    }
    .building {
        left: 0px;
        top: 0px;
        height: 40px;
        width: 40px;
        background-size: 40px 40px;
        // background-color: brown;
        position: absolute;
        &.btc {
          background-image: url('assets/bank.png');
        }
        &.etc {
          background-image: url('assets/bank2.png');
        }
    }

</style>
