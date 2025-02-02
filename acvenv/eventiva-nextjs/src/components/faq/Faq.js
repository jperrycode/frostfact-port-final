import React from 'react'
import Image from 'next/image'

import SectionName from '@/components/common/sectionTitle/SectionName'
import SectionTitle from '@/components/common/sectionTitle/SectionTitle'
import SectionTitleTwo from '@/components/common/sectionTitle/SectionTitleTwo'
import Accordion from '@/components/common/Accordion'

import ellipse_1 from "@/assets/images/home-1/ellipse-2.png"
import { faqData } from '@/lib/faqData'
import { useState } from 'react'
import { useEffect } from 'react'
import { updateFaqData } from '@/lib/axiosApi'


const Faq = ({ styleNum }) => {
    // styleNum 0 from home page 1 and home page 2
    // styleNum 1 from home page 5
    // styleNum 2 from home page 7

    let prentClass;
    let subTitle2;
    switch (styleNum) {
        case 0:
            prentClass = "faq-1 pb-50 pb-lg-100 pb-xxl-120"
            break;
        case 1:
            prentClass = 'faq-1 mb-20 mb-lg-30';
            subTitle2 = true
            break;
        case 2:
            subTitle2 = true
            break;
        default:
            break;
    }
    // ----- Change classname define in home page

    const [data, setData] = useState(faqData);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchDataAndUpdate = async () => {
            try {
                const updatedData = await updateFaqData(faqData);
                setData(updatedData);
                setLoading(false);
            } catch (err) {
                setError(err);
                setLoading(false);
            }
        };

        fetchDataAndUpdate();
    }, []);

    if (loading) return <p>Loading...</p>;
    if (error) return <p>Error loading data!</p>;

    return (
        
        <section className={`faq-section ${prentClass}`}>
            {/* <div>
                <h1>Data Loaded</h1>
                <pre>{JSON.stringify(data, null, 2)}</pre>
            </div> */}
            <div className="container">
                <div className="row gx-0 gy-lg-0 gy-30">
                    <div className="col-lg-5">
                        <div className="sticky-contents">
                            <div className="section-title section-title-style-2 mb-30 mb-lg-40 mb-xxl-60">
                                <SectionName
                                    name={"Frequently Asked Questions"}
                                    className={""}
                                />
                                {
                                    subTitle2 ?
                                        <SectionTitleTwo
                                            title={"Harmony"}
                                            subTitle={"Helpdesk"}
                                            titleClass={""}
                                            subTitleClass={"primary-text-shadow"}
                                        />
                                        :
                                        <SectionTitle
                                            title={"Venue"}
                                            subTitle={"Policies"}
                                            titleClass={""}
                                            subTitleClass={""}
                                        />

                                }
                            </div>
                            {/* -- section-title -- */}
                        </div>
                    </div>
                    {/* -- col-4 -- */}
                    <div className="col-lg-7">
                        <div className="faq-wrapper position-relative">
                            <div className="accordion" id="faq-1-accordion">
                                {
                                    data.map(({ id, ans, question }) => <Accordion key={`accordion-${id}`} id={`accordion-${id}`} ans={ans} question={question} parents_id={`faq-1-accordion`} />)
                                }

                            </div>
                            {/* <!-- .accordion --> */}

                            <div className="ellipse-image-2">
                                <Image src={ellipse_1} alt="ellipse-1" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    )
}

export default Faq