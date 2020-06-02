// JS
import React from 'react';
import ReactDOM from 'react-dom';
import './Diverging.css';
import PropTypes from 'prop-types';

const propTypes = {
  _data: PropTypes.array,
  height:PropTypes.number
};
const defaultProps = {
};

class Testing extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      data_payload:this.props._data
    }

  }

  render() {


    let jsonInput =  this.state.data_payload;
    let maxPercetTotal = 0;

    jsonInput.forEach(object_percent => 
      maxPercetTotal = ( object_percent.percentMan > maxPercetTotal  ?  object_percent.percentMan :  maxPercetTotal   )
                     ) ;
    jsonInput.forEach(object_percent => 
      maxPercetTotal = ( object_percent.percentWoman > maxPercetTotal  ?  object_percent.percentWoman :  maxPercetTotal   )
    ) ;
    maxPercetTotal = ( maxPercetTotal <= 0  ?  1 :  maxPercetTotal   )
    
    /*console.log("Total Percent General");  
    console.log(maxPercetTotal);*/

    
    const minPercent = 15;
    const maxPercent = 85;

    return (
      <div>
        <div id="title" >
        <span><span className={"dot_men"}>
                </span>Varones </span>
         
         <span><span className={'dot_women'}>
                </span>Mujeres</span>
        </div>
        <div id="ranges"  className={"gen_a"}  style={ {height: (this.props.height-10)}}>
         {
            jsonInput.map(  item => 
                                          <div className={"range_w"}>
                                              <div className={"titdvg dib"}> <span className={"fl fxCT"}> {item.label} </span> </div>     
                                              <div className={"dvggen dib"}>
                                              
                                                <div className={"genderA dib"}>
                                                  
                                                 
                                                  <div className={"genderAColor fr dib high_"} style={ {width:  ( (item.percentMan * 100 / maxPercetTotal ) > maxPercent ?  maxPercent+'%': ( (item.percentMan * 100 / maxPercetTotal ) <=0 ? 1+"%": (item.percentMan * 100 / maxPercetTotal )+'%'  )       )  } } >
                                                  </div>
                                                  <span className={"fr"} style={{"padding-right":"5%"}}>{item.percentMan}%</span>
                                                </div>

                                                <div className={"genderB dib"}>
                                                  <div className={"genderBColor fl dib high_"} style={ {width:   (item.percentWoman * 100 / maxPercetTotal ) > maxPercent ?  maxPercent+'%': ( (item.percentWoman * 100 / maxPercetTotal ) <=0 ? 1+"%": (item.percentWoman * 100 / maxPercetTotal )+'%'  ) } }>
                                                  </div>
                                                  <span className={"fl"} style={{"padding-left":"5%"}} >{item.percentWoman}%</span>
                                                </div>

                                              </div>
                                          </div>
                           )
         }
        </div>
      </div>
    );
  }
}
Testing.propTypes = propTypes;
Testing.defaultProps = defaultProps;

function diverging(slice, payload) {

  /** 
  console.log(slice);
  console.log('height'+ slice.props.height);

  console.log('height Func'+slice.height());
  console.log('width Func'+slice.width());
 */
  let data    = payload.data.content;
  let headers = payload.data.headers;


  let arraData = [];
  data.forEach((item, i) => {
    const obj = {};

          headers.forEach((column, index) => {
              const value = item[index];
              obj[column] = value === null ? '' : value;
        })
        arraData.push(obj);
  });
  
  ReactDOM.render(
    <Testing
     _data= { arraData }
     height={slice.props.height}      
    />,
    document.getElementById(slice.containerId),
  );
}

module.exports = diverging;
