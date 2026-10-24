import { Architecture } from '@/components/site/architecture'
import { Footer } from '@/components/site/footer'
import { Harness } from '@/components/site/harness'
import { Header } from '@/components/site/header'
import { Hero } from '@/components/site/hero'
import { Install } from '@/components/site/install'
import { MissionControl } from '@/components/site/mission-control'

export default function Page() {
  return (
    <>
      <Header />
      <main id="top">
        <Hero />
        <MissionControl />
        <Harness />
        <Architecture />
        <Install />
      </main>
      <Footer />
    </>
  )
}
